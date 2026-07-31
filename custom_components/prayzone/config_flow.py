from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PrayerZoneApi, PrayerZoneApiError
from .const import (
    CONF_CITY_ID,
    CONF_LANGUAGE,
    CONF_MOSQUE_ID,
    CONF_SOURCE,
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_DISTANCE,
    DOMAIN,
    LANGUAGES,
    SOURCE_CITY,
    SOURCE_MOSQUE,
)


class PrayerZoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._language = user_input[CONF_LANGUAGE]
            self._source = user_input[CONF_SOURCE]
            if self._source == SOURCE_MOSQUE:
                return await self.async_step_mosque()
            return await self.async_step_city()
        schema = vol.Schema({
            vol.Required(CONF_SOURCE, default=SOURCE_CITY): vol.In({SOURCE_CITY: "City", SOURCE_MOSQUE: "Nearby mosque"}),
            vol.Required(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGES),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_city(self, user_input=None):
        errors = {}
        if user_input is not None:
            city_id = user_input[CONF_CITY_ID].strip().lower()
            if not city_id:
                errors[CONF_CITY_ID] = "required"
            else:
                await self.async_set_unique_id(f"city:{city_id}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"PrayerZone · {city_id}", data={CONF_CITY_ID: city_id, CONF_LANGUAGE: self._language, CONF_SOURCE: SOURCE_CITY})
        return self.async_show_form(step_id="city", data_schema=vol.Schema({vol.Required(CONF_CITY_ID): str}), errors=errors)

    async def async_step_mosque(self, user_input=None):
        errors = {}
        if user_input is not None:
            mosque_id = user_input[CONF_MOSQUE_ID]
            await self.async_set_unique_id(f"mosque:{mosque_id}")
            self._abort_if_unique_id_configured()
            title = self._mosques.get(mosque_id, {}).get("title") or mosque_id
            return self.async_create_entry(title=f"PrayerZone · {title}", data={CONF_MOSQUE_ID: mosque_id, CONF_LANGUAGE: self._language, CONF_SOURCE: SOURCE_MOSQUE})
        latitude = self.hass.config.latitude
        longitude = self.hass.config.longitude
        if latitude is None or longitude is None:
            return self.async_show_form(step_id="mosque", data_schema=vol.Schema({vol.Required(CONF_MOSQUE_ID): str}), errors={"base": "no_location"})
        try:
            api = PrayerZoneApi(async_get_clientsession(self.hass))
            mosques = await api.nearby_mosques(longitude, latitude, DEFAULT_MAX_DISTANCE)
        except PrayerZoneApiError:
            return self.async_show_form(step_id="mosque", data_schema=vol.Schema({vol.Required(CONF_MOSQUE_ID): str}), errors={"base": "cannot_connect"})
        if not mosques:
            return self.async_show_form(step_id="mosque", data_schema=vol.Schema({vol.Required(CONF_MOSQUE_ID): str}), errors={"base": "no_mosques"})
        self._mosques = {item["slug"]: item for item in mosques}
        options = {slug: f"{item.get('title', slug)} ({item.get('distance', '?')} km)" for slug, item in self._mosques.items()}
        return self.async_show_form(step_id="mosque", data_schema=vol.Schema({vol.Required(CONF_MOSQUE_ID): vol.In(options)}), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PrayerZoneOptionsFlowHandler(config_entry)


class PrayerZoneOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            data = dict(self.config_entry.data)
            identifier_key = CONF_MOSQUE_ID if data.get(CONF_SOURCE) == SOURCE_MOSQUE else CONF_CITY_ID
            data[identifier_key] = user_input[identifier_key].strip().lower()
            data[CONF_LANGUAGE] = user_input[CONF_LANGUAGE]
            self.hass.config_entries.async_update_entry(self.config_entry, data=data)
            return self.async_create_entry(title="", data={})
        identifier_key = CONF_MOSQUE_ID if self.config_entry.data.get(CONF_SOURCE) == SOURCE_MOSQUE else CONF_CITY_ID
        return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Required(identifier_key, default=self.config_entry.data[identifier_key]): str, vol.Required(CONF_LANGUAGE, default=self.config_entry.data[CONF_LANGUAGE]): vol.In(LANGUAGES)}))
