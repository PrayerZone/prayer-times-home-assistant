from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PrayerZoneApi, PrayerZoneApiError
from .const import (
    CONF_CALCULATION_METHOD,
    CONF_CITY_ID,
    CONF_LANGUAGE,
    CONF_MADHAB,
    CONF_MOSQUE_ID,
    CONF_SOURCE,
    DEFAULT_CALCULATION_METHOD,
    DEFAULT_MADHAB,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_LOCATION,
    SOURCE_MOSQUE,
)


class PrayerZoneCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.identifier = entry.data.get(CONF_MOSQUE_ID if entry.data.get(CONF_SOURCE) == SOURCE_MOSQUE else CONF_CITY_ID, "")
        self.latitude = hass.config.latitude
        self.longitude = hass.config.longitude
        self.timezone = hass.config.time_zone
        self.hass = hass
        self.language = entry.data[CONF_LANGUAGE]
        self.calculation_method = entry.data.get(CONF_CALCULATION_METHOD, DEFAULT_CALCULATION_METHOD)
        self.madhab = entry.data.get(CONF_MADHAB, DEFAULT_MADHAB)
        self.source = entry.data.get(CONF_SOURCE, "city")
        self.api = PrayerZoneApi(async_get_clientsession(hass))
        super().__init__(hass, logger=__import__("logging").getLogger(__name__), name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if self.source == SOURCE_LOCATION:
                if self.latitude is None or self.longitude is None:
                    raise PrayerZoneApiError("Home Assistant latitude and longitude are required")
                return await self.api.location_prayer_times(
                    self.latitude,
                    self.longitude,
                    self.timezone,
                    self.language,
                    self.calculation_method,
                    self.madhab,
                )
            return await self.api.prayer_times(self.identifier, self.language, self.source)
        except PrayerZoneApiError as err:
            raise UpdateFailed(str(err)) from err
