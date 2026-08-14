from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import WattpilotAPI
from .const import CONF_HOST, DOMAIN


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    api = WattpilotAPI(data[CONF_HOST], data[CONF_PASSWORD])
    try:
        await api.connect()
        return {
            "title": api.name,
            "serial": api.serial,
        }
    except Exception as err:
        raise CannotConnect from err
    finally:
        await api.disconnect()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    info["serial"] or user_input[CONF_HOST]
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Unable to connect to the Wattpilot."""
