from datetime import datetime, timedelta

SCENARIOS = [
    ('hot_dry', 33, 25, 0, 4, 26.9, 75.8),
    ('cool_humid', 18, 92, 0.3, 5, 31.1, 77.2),
    ('warm_rain', 27, 88, 0.8, 8, 13.1, 80.3),
    ('windy', 23, 75, 0, 30, 18.5, 73.9),
    ('low_risk', 4, 25, 0, 2, 34.1, 74.8),
]


def raw_weather(temp, humidity, rain, wind):
    start = datetime(2026, 10, 19)
    return {'current': {'time': '2026-10-26T12:00'}, 'hourly': {
        'time': [(start+timedelta(hours=i)).isoformat(timespec='minutes') for i in range(336)],
        'temperature_2m': [temp]*336, 'relative_humidity_2m': [humidity]*336,
        'precipitation': [rain]*336, 'wind_speed_10m': [wind]*336}, 'daily': {}}
