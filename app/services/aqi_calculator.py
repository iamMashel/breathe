"""
EPA AQI calculation from raw pollutant concentrations.

OWM returns all values in µg/m³. EPA AQI uses different units per pollutant:
  - PM2.5 / PM10: µg/m³ (no conversion needed)
  - O3: ppb  → divide OWM µg/m³ by 1.9957
  - NO2: ppb → divide OWM µg/m³ by 1.8816
  - SO2: ppb → divide OWM µg/m³ by 2.6196
  - CO: ppm  → divide OWM µg/m³ by 1000 (→ mg/m³) then × (24.45/28.01)

Note: OWM gives instantaneous readings, not time-averaged values.
AQI here is a real-time proxy (NowCast-style), not a regulatory value.
"""
from dataclasses import dataclass, field


# (c_low, c_high, aqi_low, aqi_high)
_PM25_BREAKPOINTS = [
    (0.0, 9.0, 0, 50),
    (9.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 125.4, 151, 200),
    (125.5, 225.4, 201, 300),
    (225.5, 325.4, 301, 500),
]

_PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500),
]

# O3: 8-hour average, ppb
_O3_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 70, 51, 100),
    (71, 85, 101, 150),
    (86, 105, 151, 200),
    (106, 200, 201, 300),
]

# NO2: 1-hour average, ppb
_NO2_BREAKPOINTS = [
    (0, 53, 0, 50),
    (54, 100, 51, 100),
    (101, 360, 101, 150),
    (361, 649, 151, 200),
    (650, 1249, 201, 300),
    (1250, 2049, 301, 500),
]

# SO2: 1-hour average, ppb
_SO2_BREAKPOINTS = [
    (0, 35, 0, 50),
    (36, 75, 51, 100),
    (76, 185, 101, 150),
    (186, 304, 151, 200),
    (305, 604, 201, 300),
    (605, 1004, 301, 500),
]

# CO: 8-hour average, ppm
_CO_BREAKPOINTS = [
    (0.0, 4.4, 0, 50),
    (4.5, 9.4, 51, 100),
    (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200),
    (15.5, 30.4, 201, 300),
    (30.5, 50.4, 301, 500),
]

# WHO 2021 24-hour guideline values (µg/m³)
_WHO_LIMITS: dict[str, float] = {
    "pm2_5": 15.0,
    "pm10": 45.0,
    "no2": 25.0,
    "so2": 40.0,
    "o3": 100.0,  # 8-hour peak season daily max
}

AQI_CATEGORIES = [
    (0, 50, "Good", "#00E400"),
    (51, 100, "Moderate", "#FFFF00"),
    (101, 150, "Unhealthy for Sensitive Groups", "#FF7E00"),
    (151, 200, "Unhealthy", "#FF0000"),
    (201, 300, "Very Unhealthy", "#8F3F97"),
    (301, 500, "Hazardous", "#7E0023"),
]


@dataclass
class AQIResult:
    aqi: int
    category: str
    color: str
    dominant_pollutant: str
    pollutant_indices: dict[str, int] = field(default_factory=dict)
    who_guidelines_exceeded: list[str] = field(default_factory=list)


def _interpolate(c: float, breakpoints: list[tuple]) -> int:
    for c_low, c_high, aqi_low, aqi_high in breakpoints:
        if c_low <= c <= c_high:
            aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (c - c_low) + aqi_low
            return round(aqi)
    # Clamp to 500 if above all breakpoints
    return 500


def _category(aqi: int) -> tuple[str, str]:
    for low, high, label, color in AQI_CATEGORIES:
        if low <= aqi <= high:
            return label, color
    return "Hazardous", "#7E0023"


def _o3_ugm3_to_ppb(ugm3: float) -> float:
    return ugm3 / 1.9957


def _no2_ugm3_to_ppb(ugm3: float) -> float:
    return ugm3 / 1.8816


def _so2_ugm3_to_ppb(ugm3: float) -> float:
    return ugm3 / 2.6196


def _co_ugm3_to_ppm(ugm3: float) -> float:
    # µg/m³ → mg/m³ → ppm  (MW CO = 28.01, molar volume at 25°C = 24.45 L/mol)
    return (ugm3 / 1000) * (24.45 / 28.01)


def compute_aqi(components: dict) -> AQIResult:
    pm25 = components.get("pm2_5", 0.0)
    pm10 = components.get("pm10", 0.0)
    o3 = components.get("o3", 0.0)
    no2 = components.get("no2", 0.0)
    so2 = components.get("so2", 0.0)
    co = components.get("co", 0.0)

    indices = {
        "pm2_5": _interpolate(pm25, _PM25_BREAKPOINTS),
        "pm10": _interpolate(pm10, _PM10_BREAKPOINTS),
        "o3": _interpolate(_o3_ugm3_to_ppb(o3), _O3_BREAKPOINTS),
        "no2": _interpolate(_no2_ugm3_to_ppb(no2), _NO2_BREAKPOINTS),
        "so2": _interpolate(_so2_ugm3_to_ppb(so2), _SO2_BREAKPOINTS),
        "co": _interpolate(_co_ugm3_to_ppm(co), _CO_BREAKPOINTS),
    }

    dominant = max(indices, key=lambda k: indices[k])
    overall_aqi = indices[dominant]
    category, color = _category(overall_aqi)

    # Check WHO 2021 guidelines (in µg/m³ — no conversion needed here)
    who_exceeded = []
    raw = {"pm2_5": pm25, "pm10": pm10, "no2": no2, "so2": so2, "o3": o3}
    for pollutant, limit in _WHO_LIMITS.items():
        if raw.get(pollutant, 0.0) > limit:
            who_exceeded.append(pollutant)

    return AQIResult(
        aqi=overall_aqi,
        category=category,
        color=color,
        dominant_pollutant=dominant,
        pollutant_indices=indices,
        who_guidelines_exceeded=who_exceeded,
    )
