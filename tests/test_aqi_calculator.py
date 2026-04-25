import pytest
from app.services.aqi_calculator import compute_aqi, _o3_ugm3_to_ppb, _no2_ugm3_to_ppb


def _components(**overrides):
    base = {"co": 300.0, "no": 0.5, "no2": 10.0, "o3": 60.0, "so2": 5.0,
            "pm2_5": 5.0, "pm10": 20.0, "nh3": 1.0}
    return {**base, **overrides}


def test_good_air_quality():
    result = compute_aqi(_components())
    assert result.aqi <= 50
    assert result.category == "Good"


def test_high_pm25_drives_aqi_up():
    result = compute_aqi(_components(pm2_5=60.0))
    assert result.aqi > 150
    assert result.dominant_pollutant == "pm2_5"


def test_who_guideline_exceeded_for_pm25():
    result = compute_aqi(_components(pm2_5=20.0))
    assert "pm2_5" in result.who_guidelines_exceeded


def test_who_guideline_not_exceeded_when_clean():
    result = compute_aqi(_components(pm2_5=5.0))
    assert "pm2_5" not in result.who_guidelines_exceeded


def test_unit_conversions():
    # O3: 1.9957 µg/m³ → ~1 ppb
    assert abs(_o3_ugm3_to_ppb(1.9957) - 1.0) < 0.001
    # NO2: 1.8816 µg/m³ → ~1 ppb
    assert abs(_no2_ugm3_to_ppb(1.8816) - 1.0) < 0.001


def test_aqi_color_assigned():
    result = compute_aqi(_components())
    assert result.color.startswith("#")
    assert len(result.color) == 7


def test_hazardous_pm25():
    result = compute_aqi(_components(pm2_5=300.0))
    assert result.aqi >= 301
    assert result.category == "Hazardous"
