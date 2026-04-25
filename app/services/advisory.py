"""
Health advisory text generation based on EPA AQI levels.
Advisories are keyed by population group and AQI category index (0-5).
"""

_ADVISORIES: dict[str, list[str]] = {
    "general": [
        "Air quality is satisfactory. Enjoy outdoor activities freely.",
        "Air quality is acceptable. Unusually sensitive individuals may want to limit prolonged outdoor exertion.",
        "Sensitive groups may experience health effects. General public is unlikely to be affected.",
        "Everyone may begin to experience health effects. Limit prolonged outdoor exertion.",
        "Avoid prolonged outdoor exertion. Everyone should reduce outdoor activity.",
        "Health alert: serious health effects for everyone. Avoid all outdoor activity.",
    ],
    "children": [
        "Safe for all outdoor play and activities.",
        "Generally safe. Watch for unusual respiratory symptoms in sensitive children.",
        "Limit prolonged or heavy exertion outdoors. Schedule active play for the morning.",
        "Avoid prolonged or heavy outdoor exertion. Move strenuous activities indoors.",
        "Avoid all outdoor physical activity. Stay indoors.",
        "Do not go outside. Keep indoors with doors and windows closed.",
    ],
    "elderly": [
        "No precautions needed. Enjoy outdoor activities.",
        "Generally safe. Those with heart or lung conditions should note any unusual symptoms.",
        "Reduce prolonged or heavy outdoor exertion. Watch for symptoms like shortness of breath.",
        "Avoid prolonged or heavy outdoor exertion. Stay indoors during peak pollution hours.",
        "Remain indoors. Avoid all outdoor exertion. Wear N95 if going out is unavoidable.",
        "Emergency conditions. Stay indoors. Seek medical attention if experiencing symptoms.",
    ],
    "respiratory": [
        "Excellent conditions. No action needed.",
        "Keep reliever inhaler accessible. Limit very intense outdoor sessions if discomfort arises.",
        "Reduce prolonged outdoor exertion. Keep rescue medication on hand at all times.",
        "Avoid all prolonged outdoor exertion. Keep windows closed, use an air purifier if available.",
        "Remain indoors. Follow your emergency action plan. Consider N95 if going outside is necessary.",
        "Emergency conditions. Stay indoors. Have emergency contacts ready. Seek medical advice.",
    ],
    "athletes": [
        "Ideal conditions for training and competition.",
        "Generally fine for training. Consider shortening very high-intensity sessions if you feel discomfort.",
        "Shorten or reschedule high-intensity sessions. Rest more between intervals.",
        "Avoid high-intensity outdoor training. Move workouts indoors.",
        "Cancel all outdoor training. Indoor alternatives only.",
        "No outdoor activity of any kind. All sessions must move indoors.",
    ],
    "pregnant": [
        "No restrictions. Normal outdoor activity is fine.",
        "Generally safe. Avoid prolonged intense outdoor activity if experiencing any respiratory discomfort.",
        "Limit prolonged heavy outdoor exertion. Avoid high-traffic and congested areas.",
        "Avoid prolonged outdoor activity. Stay indoors in filtered-air environments where possible.",
        "Remain indoors. Avoid any outdoor exposure.",
        "Stay indoors. Seek medical evaluation if experiencing any respiratory or cardiovascular symptoms.",
    ],
}

_AQI_BAND_INDEX = [
    (0, 50, 0),
    (51, 100, 1),
    (101, 150, 2),
    (151, 200, 3),
    (201, 300, 4),
    (301, 500, 5),
]


def _band_index(aqi: int) -> int:
    for low, high, idx in _AQI_BAND_INDEX:
        if low <= aqi <= high:
            return idx
    return 5


def get_advisories(aqi: int) -> dict[str, str]:
    idx = _band_index(aqi)
    return {group: messages[idx] for group, messages in _ADVISORIES.items()}


def get_outdoor_safety_score(aqi: int, temperature_c: float, humidity_pct: float) -> dict:
    """
    Composite outdoor safety score (0-100) combining AQI, temperature, and humidity.
    100 = perfect conditions, 0 = do not go outside.
    """
    # AQI contribution: linear scale, AQI 0 → 100 pts, AQI 300+ → 0 pts
    aqi_score = max(0.0, 100 - (aqi / 3))

    # Temperature penalty: ideal is 15-25°C
    if 15 <= temperature_c <= 25:
        temp_penalty = 0
    elif temperature_c < 0 or temperature_c > 40:
        temp_penalty = 25
    elif temperature_c < 10 or temperature_c > 35:
        temp_penalty = 15
    else:
        temp_penalty = 5

    # Humidity penalty: ideal is 30-60%
    if 30 <= humidity_pct <= 60:
        humidity_penalty = 0
    elif humidity_pct > 85 or humidity_pct < 10:
        humidity_penalty = 15
    else:
        humidity_penalty = 7

    score = max(0, min(100, round(aqi_score - temp_penalty - humidity_penalty)))

    if score >= 80:
        label = "Excellent"
    elif score >= 60:
        label = "Good"
    elif score >= 40:
        label = "Fair"
    elif score >= 20:
        label = "Poor"
    else:
        label = "Dangerous"

    return {"score": score, "label": label}
