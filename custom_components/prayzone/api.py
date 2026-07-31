from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_BASE


class PrayerZoneApiError(Exception):
    """Raised when the PrayerZone API cannot return valid data."""


class PrayerZoneApi:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def prayer_times(self, identifier: str, language: str, source: str) -> dict[str, Any]:
        resource = "mosques" if source == "mosque" else "cities"
        url = f"{API_BASE}/api/public/{resource}/{identifier}/prayer-times"
        try:
            async with self._session.get(url, params={"lang": language}) as response:
                if response.status >= 400:
                    raise PrayerZoneApiError(f"API returned HTTP {response.status}")
                payload = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise PrayerZoneApiError("Unable to read prayer times from pray.zone") from err
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
            raise PrayerZoneApiError("The API returned an unexpected response")
        return payload

    async def city_prayer_times(self, city_id: str, language: str) -> dict[str, Any]:
        return await self.prayer_times(city_id, language, "city")

    async def mosque_prayer_times(self, mosque_id: str, language: str) -> dict[str, Any]:
        return await self.prayer_times(mosque_id, language, "mosque")

    async def nearby_mosques(self, longitude: float, latitude: float, max_distance: int) -> list[dict[str, Any]]:
        try:
            async with self._session.get(
                f"{API_BASE}/api/mosques/nearby",
                params={"longitude": longitude, "latitude": latitude, "maxDistance": max_distance},
            ) as response:
                if response.status >= 400:
                    raise PrayerZoneApiError(f"API returned HTTP {response.status}")
                payload = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise PrayerZoneApiError("Unable to discover nearby mosques from pray.zone") from err
        if not isinstance(payload, list):
            raise PrayerZoneApiError("The API returned an unexpected mosque list")
        return [item for item in payload if isinstance(item, dict) and item.get("slug")]
