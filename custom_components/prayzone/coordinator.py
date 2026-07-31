from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PrayerZoneApi, PrayerZoneApiError
from .const import CONF_CITY_ID, CONF_LANGUAGE, DEFAULT_SCAN_INTERVAL, DOMAIN


class PrayerZoneCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.city_id = entry.data[CONF_CITY_ID]
        self.language = entry.data[CONF_LANGUAGE]
        self.api = PrayerZoneApi(async_get_clientsession(hass))
        super().__init__(hass, logger=__import__("logging").getLogger(__name__), name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.city_prayer_times(self.city_id, self.language)
        except PrayerZoneApiError as err:
            raise UpdateFailed(str(err)) from err
