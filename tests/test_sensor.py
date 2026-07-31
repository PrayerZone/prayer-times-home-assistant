from types import SimpleNamespace

from custom_components.prayzone.sensor import (
    NextPrayerNameSensor,
    NextPrayerSensor,
    _device_info,
    _prayers,
    _time_value,
)


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


def test_prayer_ids_are_stable_when_names_are_translated():
    value = coordinator()
    value.data["data"]["prayerTimes"] = [{"id": "Fajr", "name": "Aube", "time": "05:00", "isNext": True}]
    assert _prayers(value)["fajr"]["name"] == "Aube"


def test_explicit_next_prayer_supports_tomorrow():
    value = coordinator()
    value.data["data"]["nextPrayer"] = {"id": "Fajr", "name": "Fajr", "date": "2026-08-02", "time": "04:58"}
    sensor = NextPrayerSensor(value, value.entry)
    name_sensor = NextPrayerNameSensor(value, value.entry)
    assert sensor.native_value.isoformat() == "2026-08-02T04:58:00+02:00"
    assert name_sensor.native_value == "Fajr"
