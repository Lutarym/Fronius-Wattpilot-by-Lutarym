"""Einrichtungsdialog fuer den Wattpilot."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import WattpilotAPI
from .const import CONF_HOST, CONF_PASSWORD, DOMAIN

STEP_USER_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): TextSelector(
        TextSelectorConfig(type=TextSelectorType.TEXT)
    ),
    vol.Required(CONF_PASSWORD): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
})


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Prueft, ob eine Verbindung mit den Angaben moeglich ist."""
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
    """Fuehrt durch die Einrichtung."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
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
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Startet die erneute Anmeldung, wenn das Passwort nicht mehr passt."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            data = {**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
            try:
                await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(entry, data=data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Verbindung zum Wattpilot nicht moeglich."""
