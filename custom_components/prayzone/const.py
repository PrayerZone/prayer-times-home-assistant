from datetime import timedelta

DOMAIN = "prayzone"
NAME = "PrayerZone"
CONF_CITY_ID = "city_id"
CONF_MOSQUE_ID = "mosque_id"
CONF_LANGUAGE = "language"
CONF_SOURCE = "source"
CONF_MAX_DISTANCE = "max_distance"
CONF_CALCULATION_METHOD = "calculation_method"
CONF_MADHAB = "madhab"
SOURCE_CITY = "city"
SOURCE_MOSQUE = "mosque"
SOURCE_LOCATION = "location"
DEFAULT_LANGUAGE = "en"
DEFAULT_MAX_DISTANCE = 5000
DEFAULT_CALCULATION_METHOD = "auto"
DEFAULT_MADHAB = "auto"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
API_BASE = "https://pray.zone"
ATTRIBUTION = "Prayer times powered by pray.zone"
LANGUAGES = {"en": "English", "fr": "Français", "ar": "العربية", "bn": "বাংলা", "de": "Deutsch", "es": "Español", "it": "Italiano", "pt": "Português"}
PRAYER_KEYS = ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
CALCULATION_METHODS = {
    "auto": "Automatic (location default)",
    "MuslimWorldLeague": "Muslim World League",
    "Egyptian": "Egyptian General Authority",
    "Karachi": "University of Islamic Sciences, Karachi",
    "UmmAlQura": "Umm al-Qura University, Makkah",
    "NorthAmerica": "Islamic Society of North America",
    "Uoif": "Union of Islamic Organisations of France",
    "Turkey": "Diyanet (Turkey)",
    "Morocco": "Morocco",
    "Algerian": "Algeria",
    "LondonCentralMosque": "London Central Mosque",
}
MADHABS = {"auto": "Automatic", "Shafi": "Shafi", "Hanafi": "Hanafi"}
