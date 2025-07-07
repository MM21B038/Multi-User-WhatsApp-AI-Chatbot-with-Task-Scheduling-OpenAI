import pytz
import requests
from datetime import datetime

def get_location_from_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status()
        data = response.json()

        loc_parts = data.get("loc", "").split(",")

        return {
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country", ""),
            "latitude": loc_parts[0] if len(loc_parts) == 2 else "",
            "longitude": loc_parts[1] if len(loc_parts) == 2 else "",
            "timezone": data.get("timezone", "")
        }
    except Exception as e:
        return {"error": str(e)}


def get_current_datetime_by_timezone(timezone: str):
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return {
            "timezone": timezone,
            "current_time": now.isoformat()
        }
    except Exception as e:
        return {"error": str(e)}