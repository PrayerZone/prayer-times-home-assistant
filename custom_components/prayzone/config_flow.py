from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_CITY_ID, CONF_LANGUAGE, DEFAULT_LANGUAGE, DOMAIN, LANGUAGES


class PrayerZoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            city_id = user_input[CONF_CITY_ID].strip().lower()
            if not city_id:
                errors[CONF_CITY_ID] = "required"
            else:
                await self.async_set_unique_id(f"{city_id}:{user_input[CONF_LANGUAGE]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"PrayerZone · {city_id}", data={CONF_CITY_ID: city_id, CONF_LANGUAGE: user_input[CONF_LANGUAGE]})
        schema = vol.Schema({vol.Required(CONF_CITY_ID): str, vol.Required(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGES)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PrayerZoneOptionsFlowHandler(config_entry)


class PrayerZoneOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(self.config_entry, data={CONF_CITY_ID: user_input[CONF_CITY_ID].strip().lower(), CONF_LANGUAGE: user_input[CONF_LANGUAGE]})
            return self.async_create_entry(title="", data={})
        return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Required(CONF_CITY_ID, default=self.config_entry.data[CONF_CITY_ID]): str, vol.Required(CONF_LANGUAGE, default=self.config_entry.data[CONF_LANGUAGE]): vol.In(LANGUAGES)}))
