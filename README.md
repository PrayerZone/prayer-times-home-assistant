# PrayerZone for Home Assistant

Official Home Assistant custom integration for prayer times from the [pray.zone API](https://pray.zone/api).

It creates sensors for Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha, the next prayer, and the Qibla bearing. The integration refreshes automatically every 15 minutes and uses Home Assistant's device and entity registry.

## Install with HACS

1. In HACS, open **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/PrayerZone/prayer-times-home-assistant` as an **Integration**.
3. Install **PrayerZone**, restart Home Assistant, and add **PrayerZone** from **Settings → Devices & services**.
4. Enter a city identifier such as `paris` and choose the display language.

## Attribution

If prayer data is displayed publicly, attribution is mandatory. Keep the entity attribution and include a visible link to [pray.zone](https://pray.zone/).

## Development

```bash
python -m pytest
ruff check .
```

This project is MIT licensed. PrayerZone API data remains subject to the API attribution requirement.
