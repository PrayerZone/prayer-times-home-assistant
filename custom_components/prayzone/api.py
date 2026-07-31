from __future__ import annotations

from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo

from aiohttp import ClientError, ClientSession

from .const import API_BASE, COORDINATES_API_BASE


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

    async def location_prayer_times(self, latitude: float, longitude: float, timezone: str) -> dict[str, Any]:
        """Calculate prayer times for Home Assistant's configured location."""
        try:
            local_date = datetime.now(ZoneInfo(timezone)).date().isoformat()
            async with self._session.get(
                f"{COORDINATES_API_BASE}/prayer-times-by-coordinates",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone,
                    "calculationMethod": "MuslimWorldLeague",
                    "date": local_date,
                },
            ) as response:
                if response.status >= 400:
                    raise PrayerZoneApiError(f"API returned HTTP {response.status}")
                payload = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise PrayerZoneApiError("Unable to calculate prayer times for the Home Assistant location") from err
        if not isinstance(payload, dict) or not isinstance(payload.get("prayerTimes"), dict):
            raise PrayerZoneApiError("The coordinates API returned an unexpected response")
        # Keep the same shape as the public city/mosque endpoints.
        return {"type": "location", "city": {"name": "Home Assistant location", "timezone": timezone}, "data": {
            "date": payload.get("date", local_date), "timezone": timezone,
            "prayerTimes": [
                {"name": name, "time": value, "isNext": False}
                for name, value in payload["prayerTimes"].items()
            ],
            "qibla": None,
            "calculation": payload.get("calculationParameters"),
        }}

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
