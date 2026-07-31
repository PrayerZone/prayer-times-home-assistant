from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PrayerZoneApi, PrayerZoneApiError
from .const import (
    CONF_CITY_ID,
    CONF_LANGUAGE,
    CONF_MOSQUE_ID,
    CONF_SOURCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_MOSQUE,
)


class PrayerZoneCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.identifier = entry.data.get(CONF_MOSQUE_ID if entry.data.get(CONF_SOURCE) == SOURCE_MOSQUE else CONF_CITY_ID, "")
        self.language = entry.data[CONF_LANGUAGE]
        self.source = entry.data.get(CONF_SOURCE, "city")
        self.api = PrayerZoneApi(async_get_clientsession(hass))
        super().__init__(hass, logger=__import__("logging").getLogger(__name__), name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.prayer_times(self.identifier, self.language, self.source)
        except PrayerZoneApiError as err:
            raise UpdateFailed(str(err)) from err
