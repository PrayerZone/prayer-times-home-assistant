from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, PRAYER_KEYS, SOURCE_LOCATION, SOURCE_MOSQUE
from .coordinator import PrayerZoneCoordinator


def _prayers(coordinator):
    raw = coordinator.data.get("data", {}).get("prayerTimes", [])
    return {
        str(item.get("id") or item.get("name", "")).lower(): item
        for item in raw
        if isinstance(item, dict)
    }


def _time_value(coordinator, item):
    if not item or not item.get("time"):
        return None
    value = str(item["time"])
    try:
        if "T" in value:
            return datetime.fromisoformat(value)
        date = coordinator.data.get("data", {}).get("date")
        timezone = coordinator.data.get("data", {}).get("timezone", "UTC")
        if not date:
            return None
        try:
            tz = ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo("UTC")
        return datetime.fromisoformat(f"{date}T{value}").replace(tzinfo=tz)
    except (TypeError, ValueError):
        return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: PrayerZoneCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [PrayerSensor(coordinator, entry, key) for key in PRAYER_KEYS]
    entities += [NextPrayerSensor(coordinator, entry), NextPrayerNameSensor(coordinator, entry), QiblaSensor(coordinator, entry), LocationSensor(coordinator, entry)]
    for item in coordinator.data.get("data", {}).get("prayerTimes", []):
        name = str(item.get("name", ""))
        key = name.lower().replace(" ", "_")
        if key not in PRAYER_KEYS and ("iqama" in key or "jumua" in key or "jumu" in key):
            entities.append(PrayerSensor(coordinator, entry, key, name))
    async_add_entities(entities)


class PrayerSensor(CoordinatorEntity[PrayerZoneCoordinator], SensorEntity):
    _attr_device_class = "timestamp"
    _attr_icon = "mdi:mosque"

    def __init__(self, coordinator, entry, key, name=None):
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name or key.replace("_", " ").title()
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        return _time_value(self.coordinator, _prayers(self.coordinator).get(self._key))

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self.coordinator.entry)


class NextPrayerSensor(PrayerSensor):
    _attr_icon = "mdi:weather-sunset-up"

    def __init__(self, coordinator, entry):
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._attr_name = "Next prayer"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        explicit = self.coordinator.data.get("data", {}).get("nextPrayer")
        if isinstance(explicit, dict) and explicit.get("date") and explicit.get("time"):
            timezone = self.coordinator.data.get("data", {}).get("timezone", "UTC")
            try:
                return datetime.fromisoformat(f"{explicit['date']}T{explicit['time']}").replace(tzinfo=ZoneInfo(timezone))
            except (TypeError, ValueError, ZoneInfoNotFoundError):
                pass
        for item in _prayers(self.coordinator).values():
            if item.get("isNext"):
                return _time_value(self.coordinator, item)
        return None

    @property
    def extra_state_attributes(self):
        explicit = self.coordinator.data.get("data", {}).get("nextPrayer") or {}
        return {"prayer": explicit.get("name") or next((item.get("name") for item in _prayers(self.coordinator).values() if item.get("isNext")), None), "source": "https://pray.zone/"}


class QiblaSensor(CoordinatorEntity[PrayerZoneCoordinator], SensorEntity):
    _attr_native_unit_of_measurement = "°"
    _attr_icon = "mdi:compass"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_qibla"
        self._attr_name = "Qibla bearing"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        qibla = self.coordinator.data.get("data", {}).get("qibla") or {}
        return qibla.get("bearing")

    @property
    def extra_state_attributes(self):
        qibla = self.coordinator.data.get("data", {}).get("qibla") or {}
        return {"direction": qibla.get("direction"), "distance_to_mecca_km": qibla.get("distanceToMeccaKm"), "source": "https://pray.zone/"}

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self.coordinator.entry)


class NextPrayerNameSensor(CoordinatorEntity[PrayerZoneCoordinator], SensorEntity):
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_name"
        self._attr_name = "Next prayer name"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        explicit = self.coordinator.data.get("data", {}).get("nextPrayer") or {}
        return explicit.get("name") or next((item.get("name") for item in _prayers(self.coordinator).values() if item.get("isNext")), None)

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self.coordinator.entry)


class LocationSensor(CoordinatorEntity[PrayerZoneCoordinator], SensorEntity):
    _attr_icon = "mdi:map-marker"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_location"
        self._attr_name = "Location"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        location = _location(self.coordinator)
        return location.get("name") or location.get("title") or _fallback_location_name(self.coordinator)

    @property
    def extra_state_attributes(self):
        location = _location(self.coordinator)
        return {key: value for key, value in location.items() if key in {"id", "city", "country", "countryCode", "address", "timezone", "coordinates", "latitude", "longitude", "altitude"}}

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self.coordinator.entry)


def _device_info(coordinator, entry) -> DeviceInfo:
    location = _location(coordinator)
    name = location.get("title") or location.get("name") or _fallback_location_name(coordinator)
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"PrayerZone · {name}",
        manufacturer="PrayerZone",
        model="Prayer times API",
        configuration_url="https://pray.zone/api",
    )


def _location(coordinator):
    key = "mosque" if coordinator.source == SOURCE_MOSQUE else "location" if coordinator.source == SOURCE_LOCATION else "city"
    return coordinator.data.get(key, {}) or {}


def _fallback_location_name(coordinator):
    return "Home location" if coordinator.source == SOURCE_LOCATION else coordinator.identifier
