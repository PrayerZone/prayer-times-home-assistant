import tempfile
import unittest
from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant

from custom_components.prayzone.config_flow import PrayerZoneConfigFlow
from custom_components.prayzone.const import CONF_CITY_ID, CONF_LANGUAGE, CONF_SOURCE, SOURCE_CITY


class TestPrayerZoneConfigFlow(unittest.IsolatedAsyncioTestCase):
    async def test_city_configuration(self):
        flow = PrayerZoneConfigFlow()
        flow.hass = HomeAssistant(tempfile.mkdtemp())

        first = await flow.async_step_user()
        assert first["step_id"] == "user"
        second = await flow.async_step_user({CONF_SOURCE: SOURCE_CITY, CONF_LANGUAGE: "fr"})
        assert second["step_id"] == "city"
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = lambda: None
        result = await flow.async_step_city({CONF_CITY_ID: " Paris "})

        assert result["type"] == "create_entry"
        assert result["data"][CONF_CITY_ID] == "paris"
        assert result["data"][CONF_LANGUAGE] == "fr"
