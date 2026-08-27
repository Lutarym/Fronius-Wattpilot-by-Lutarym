"""Fronius Wattpilot by Lutarym."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .api import WattpilotAPI
from .const import (
    ATTR_PROPERTY,
    ATTR_VALUE,
    CONF_HOST,
    CONF_PASSWORD,
    DOMAIN,
    SERVICE_SET_PROPERTY,
)
from .coordinator import WattpilotCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "sensor",
    "binary_sensor",
    "number",
    "select",
    "switch",
    "text",
    "button",
]

SET_PROPERTY_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
    vol.Required(ATTR_PROPERTY): cv.string,
    vol.Required(ATTR_VALUE): vol.Any(str, int, float, bool),
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richtet einen Wattpilot aus einem Konfigurationseintrag ein."""
    api = WattpilotAPI(entry.data[CONF_HOST], entry.data[CONF_PASSWORD])
    coordinator = WattpilotCoordinator(hass, api, entry)
    await coordinator.async_connect()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Wird die Einstellung geaendert, muss neu geladen werden, damit die
    # Entitaetenliste neu aufgebaut wird.
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entlaedt einen Konfigurationseintrag."""
    coordinator: WattpilotCoordinator = entry.runtime_data
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await coordinator.async_shutdown_connection()
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Laedt einen Konfigurationseintrag neu."""
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(hass: HomeAssistant) -> None:
    """Registriert den Dienst zum Setzen beliebiger Properties."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_PROPERTY):
        return

    async def handle_set_property(call: ServiceCall) -> None:
        """Setzt eine beliebige Property auf dem gewaehlten Geraet."""
        device_id = call.data["device_id"]
        registry = dr.async_get(hass)
        device = registry.async_get(device_id)
        if device is None:
            raise ValueError(f"Unbekanntes Geraet: {device_id}")

        for entry_id in device.config_entries:
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry is None or entry.domain != DOMAIN:
                continue
            coordinator: WattpilotCoordinator = entry.runtime_data
            await coordinator.async_set_property(
                call.data[ATTR_PROPERTY], call.data[ATTR_VALUE]
            )
            return

        raise ValueError(f"Geraet gehoert nicht zu {DOMAIN}: {device_id}")

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PROPERTY,
        handle_set_property,
        schema=SET_PROPERTY_SCHEMA,
    )
