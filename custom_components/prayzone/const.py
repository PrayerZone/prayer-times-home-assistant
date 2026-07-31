from datetime import timedelta

DOMAIN = "prayzone"
NAME = "PrayerZone"
CONF_CITY_ID = "city_id"
CONF_MOSQUE_ID = "mosque_id"
CONF_LANGUAGE = "language"
CONF_SOURCE = "source"
CONF_MAX_DISTANCE = "max_distance"
SOURCE_CITY = "city"
SOURCE_MOSQUE = "mosque"
SOURCE_LOCATION = "location"
DEFAULT_LANGUAGE = "en"
DEFAULT_MAX_DISTANCE = 5000
DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
API_BASE = "https://pray.zone"
COORDINATES_API_BASE = "https://api.pray.zone/v1"
ATTRIBUTION = "Prayer times powered by pray.zone"
LANGUAGES = {"en": "English", "fr": "Français", "ar": "العربية", "bn": "বাংলা", "de": "Deutsch", "es": "Español", "it": "Italiano", "pt": "Português"}
PRAYER_KEYS = ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
