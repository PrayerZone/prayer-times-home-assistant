# PrayerZone for Home Assistant

Official Home Assistant custom integration for prayer times from the [pray.zone API](https://pray.zone/api).

It creates sensors for Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha, the next prayer, the next prayer name, location metadata, and Qibla bearing. You can use a city, a nearby mosque, or Home Assistant's own GPS location (calculated through the pray.zone coordinates API). If the API adds Iqama or Jumu'a fields, those timestamp sensors are exposed automatically. The integration refreshes automatically every 15 minutes and groups all entities under one Home Assistant device.

The current public API exposes daily prayer times, Qibla, calculation metadata, city data, mosque data, and nearby-mosque discovery. Iqama and Jumu'a sensors are deliberately created only when those fields are returned by the API.

## Install with HACS

1. In HACS, open **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/PrayerZone/prayer-times-home-assistant` as an **Integration**.
3. Install **PrayerZone**, restart Home Assistant, and add **PrayerZone** from **Settings → Devices & services**.
4. Choose your Home Assistant location, a city identifier such as `paris`, or a nearby mosque using Home Assistant's configured GPS coordinates.

For the Home Assistant location mode, the integration automatically uses the configured latitude, longitude, and timezone. Its options let you keep the location-default calculation or select a recognized calculation method and choose the Shafi or Hanafi Asr convention.

## Dashboard example

After setup, add an Entities card and select the PrayerZone device. A compact manual card can look like this (adjust entity IDs to your installation):

```yaml
type: entities
title: Prayer times
entities:
  - sensor.prayerzone_fajr
  - sensor.prayerzone_dhuhr
  - sensor.prayerzone_asr
  - sensor.prayerzone_maghrib
  - sensor.prayerzone_isha
  - sensor.prayerzone_next_prayer
  - sensor.prayerzone_next_prayer_name
  - sensor.prayerzone_qibla_bearing
```

## Automations

Copy one of the included blueprints from `blueprints/automation/prayerzone/` into your Home Assistant blueprints folder to announce the next prayer or play an adhan on a media player. The timestamp and next-prayer-name entities can also be used directly in automations.

## Attribution

If prayer data is displayed publicly, attribution is mandatory. Keep the entity attribution and include a visible link to [pray.zone](https://pray.zone/).

## Development

```bash
python -m pytest
python -m ruff check custom_components tests
```

This project is MIT licensed. PrayerZone API data remains subject to the API attribution requirement.
