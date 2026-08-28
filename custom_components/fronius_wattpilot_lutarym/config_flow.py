"""Einrichtungsdialog fuer den Wattpilot."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    BooleanSelector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import WattpilotAPI
from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    DEFAULT_ONLY_AVAILABLE,
    DOMAIN,
    OPT_ONLY_AVAILABLE,
)

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
    api = WattpilotAPI(hass, data[CONF_HOST], data[CONF_PASSWORD])
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Gibt die Einstellungsseite zurueck."""
        return OptionsFlow()

    def _speichern_und_beenden(
        self, entry: config_entries.ConfigEntry, **kwargs: Any
    ) -> config_entries.ConfigFlowResult:
        """Speichert die Aenderung und beendet den Dialog.

        Seit Home Assistant 2026.6 darf eine Integration nicht gleichzeitig
        einen Update-Listener haben und im Dialog selbst neu laden. Sonst
        wird zweimal neu geladen. Diese Integration braucht den Listener
        fuer die Einstellungsseite, deshalb wird hier nur gespeichert.
        Das Neuladen uebernimmt der Listener.

        Aeltere Home-Assistant-Fassungen kennen die neue Methode noch
        nicht. Fuer die wird auf die bisherige zurueckgegriffen.
        """
        if hasattr(self, "async_update_and_abort"):
            return self.async_update_and_abort(entry, **kwargs)
        return self.async_update_reload_and_abort(entry, **kwargs)

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
                # reload_on_update abschalten, weil das Neuladen
                # bereits der Update-Listener uebernimmt.
                self._abort_if_unique_id_configured(reload_on_update=False)
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Aendert IP-Adresse und Passwort eines bereits eingerichteten Geraets.

        Wird gebraucht, wenn der Wattpilot eine neue IP-Adresse bekommen hat
        oder das Passwort in der App geaendert wurde.
        """
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                # Es muss dasselbe Geraet bleiben. Zeigt die neue Adresse auf
                # einen anderen Wattpilot, wird abgebrochen, damit nicht die
                # Verlaeufe zweier Geraete vermischt werden.
                await self.async_set_unique_id(
                    info["serial"] or user_input[CONF_HOST]
                )
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self._speichern_und_beenden(
                    entry,
                    data_updates=user_input,
                )

        # Die bisherige Adresse ist vorausgefuellt, das Passwort nicht.
        schema = vol.Schema({
            vol.Required(
                CONF_HOST,
                default=entry.data.get(CONF_HOST, ""),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
            vol.Required(CONF_PASSWORD): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
            description_placeholders={"device": entry.title},
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Startet die erneute Anmeldung, wenn das Passwort nicht mehr passt."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Fragt nur das Passwort erneut ab, die Adresse bleibt bestehen."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            daten = {**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
            try:
                await validate_input(self.hass, daten)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self._speichern_und_beenden(
                    entry,
                    data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }),
            errors=errors,
            description_placeholders={"device": entry.title},
        )


class CannotConnect(HomeAssistantError):
    """Verbindung zum Wattpilot nicht moeglich."""


class OptionsFlow(config_entries.OptionsFlow):
    """Einstellungen, die nach der Einrichtung geaendert werden koennen."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        aktuell = self.config_entry.options.get(
            OPT_ONLY_AVAILABLE, DEFAULT_ONLY_AVAILABLE
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(OPT_ONLY_AVAILABLE, default=aktuell): BooleanSelector(),
            }),
        )
