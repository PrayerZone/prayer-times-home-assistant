import asyncio

from custom_components.prayzone.api import PrayerZoneApi


class FakeResponse:
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def json(self):
        return [{"title": "Mosque", "slug": "paris_mosque", "distance": 1.2}]


class FakeSession:
    def get(self, url, params=None):
        assert url.endswith("/api/mosques/nearby")
        assert params == {"longitude": 2.3, "latitude": 48.8, "maxDistance": 5000}
        return FakeResponse()


class CoordinatesResponse(FakeResponse):
    async def json(self):
        return {"type": "coordinates", "location": {"timezone": "Europe/Paris"}, "data": {"prayerTimes": []}}


class CoordinatesSession:
    def get(self, url, params=None):
        assert url.endswith("/api/public/coordinates/prayer-times")
        assert params == {
            "latitude": 48.8,
            "longitude": 2.3,
            "timezone": "Europe/Paris",
            "lang": "fr",
            "calculationMethod": "Uoif",
            "madhab": "Hanafi",
        }
        return CoordinatesResponse()


def test_nearby_mosques_contract():
    result = asyncio.run(PrayerZoneApi(FakeSession()).nearby_mosques(2.3, 48.8, 5000))
    assert result[0]["slug"] == "paris_mosque"


def test_coordinates_contract_and_options():
    result = asyncio.run(
        PrayerZoneApi(CoordinatesSession()).location_prayer_times(
            48.8, 2.3, "Europe/Paris", "fr", "Uoif", "Hanafi"
        )
    )
    assert result["type"] == "location"
