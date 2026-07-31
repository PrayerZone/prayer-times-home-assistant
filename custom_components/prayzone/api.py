from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession

from .const import API_BASE


class PrayerZoneApiError(Exception):
    """Raised when the PrayerZone API cannot return valid data."""


class PrayerZoneApi:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def city_prayer_times(self, city_id: str, language: str) -> dict[str, Any]:
        url = f"{API_BASE}/api/public/cities/{city_id}/prayer-times"
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
