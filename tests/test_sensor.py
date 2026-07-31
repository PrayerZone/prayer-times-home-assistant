from types import SimpleNamespace

from custom_components.prayzone.sensor import _device_info, _prayers, _time_value


def coordinator():
    return SimpleNamespace(
        source="city",
        identifier="paris",
        entry=SimpleNamespace(entry_id="entry-1"),
        data={
            "city": {"name": "Paris", "country": "France"},
            "data": {
                "date": "2026-08-01",
                "timezone": "Europe/Paris",
                "prayerTimes": [{"name": "Fajr", "time": "05:00", "isNext": True}],
            },
        },
    )


def test_prayer_time_is_timezone_aware():
    value = _time_value(coordinator(), _prayers(coordinator())["fajr"])
    assert value.isoformat() == "2026-08-01T05:00:00+02:00"


def test_device_info_groups_entities():
    info = _device_info(coordinator(), coordinator().entry)
    assert info["name"] == "PrayerZone · Paris"
    assert ("prayzone", "entry-1") in info["identifiers"]
