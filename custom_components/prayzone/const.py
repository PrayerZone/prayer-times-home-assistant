from datetime import timedelta

DOMAIN = "prayzone"
NAME = "PrayerZone"
CONF_CITY_ID = "city_id"
CONF_LANGUAGE = "language"
DEFAULT_LANGUAGE = "en"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
API_BASE = "https://pray.zone"
ATTRIBUTION = "Prayer times powered by pray.zone"
LANGUAGES = {"en": "English", "fr": "Français", "ar": "العربية", "bn": "বাংলা", "de": "Deutsch", "es": "Español", "it": "Italiano", "pt": "Português"}
PRAYER_KEYS = ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
