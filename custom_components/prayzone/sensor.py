from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, PRAYER_KEYS
from .coordinator import PrayerZoneCoordinator


def _prayers(coordinator):
    raw = coordinator.data.get("data", {}).get("prayerTimes", [])
    return {str(item.get("name", "")).lower(): item for item in raw if isinstance(item, dict)}


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
    entities += [NextPrayerSensor(coordinator, entry), QiblaSensor(coordinator, entry)]
    async_add_entities(entities)


class PrayerSensor(CoordinatorEntity[PrayerZoneCoordinator], SensorEntity):
    _attr_device_class = "timestamp"
    _attr_icon = "mdi:mosque"

    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = key.replace("_", " ").title()
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        return _time_value(self.coordinator, _prayers(self.coordinator).get(self._key))


class NextPrayerSensor(PrayerSensor):
    _attr_icon = "mdi:weather-sunset-up"

    def __init__(self, coordinator, entry):
        CoordinatorEntity.__init__(self, coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._attr_name = "Next prayer"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        for item in _prayers(self.coordinator).values():
            if item.get("isNext"):
                return _time_value(self.coordinator, item)
        return None

    @property
    def extra_state_attributes(self):
        return {"prayer": next((item.get("name") for item in _prayers(self.coordinator).values() if item.get("isNext")), None), "source": "https://pray.zone/"}


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
        return self.coordinator.data.get("data", {}).get("qibla", {}).get("bearing")
