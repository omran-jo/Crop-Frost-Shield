import requests

def fetch_weather(lat, lon):
    try:
        #الاتصال بAPI
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&forecast_days=1"
        data = requests.get(url).json()['hourly']

        #استخراج القيم الحرجة (أدنى حرارة، متوسط الرياح، أعلى رطوبة)
        return {
            'temp_night': min(data['temperature_2m'][:12]),
            'wind_speed': sum(data['wind_speed_10m'][:12])/12,
            'humidity': max(data['relative_humidity_2m'][:12])
        }
    except: return None