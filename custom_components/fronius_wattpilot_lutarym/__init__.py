"""Fronius Wattpilot by Lutarym."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

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
    api = WattpilotAPI(hass, entry.data[CONF_HOST], entry.data[CONF_PASSWORD])
    coordinator = WattpilotCoordinator(hass, api, entry)
    await coordinator.async_connect()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Eintraege aus frueheren Fassungen entfernen, die jetzt nicht mehr
    # angelegt werden. Home Assistant laesst sie sonst dauerhaft als
    # "Nicht verfuegbar" in der Liste stehen.
    _entfernte_altlasten(hass, entry, coordinator)

    # Wird die Einstellung geaendert, muss neu geladen werden, damit die
    # Entitaetenliste neu aufgebaut wird.
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _register_services(hass)
    return True


def _entfernte_altlasten(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: WattpilotCoordinator,
) -> None:
    """Loescht Registereintraege, die nicht mehr angelegt werden.

    Das betrifft zwei Faelle: Entitaeten aus aelteren Fassungen dieser
    Integration und Werte, die das Geraet gar nicht liefert.

    Wurde die Verfuegbarkeitspruefung abgeschaltet oder hat sie nichts
    erkannt, wird nichts geloescht. Sonst koennte ein einmaliger
    Aussetzer beim Verbinden den Verlauf einer Entitaet vernichten.
    """
    if not coordinator.filter_entities or not coordinator.available_keys:
        return

    if not coordinator.angelegte_kennungen:
        _LOGGER.debug("Keine Entitaeten angelegt, es wird nicht aufgeraeumt")
        return

    registry = er.async_get(hass)
    veraltet = [
        eintrag
        for eintrag in er.async_entries_for_config_entry(registry, entry.entry_id)
        if eintrag.unique_id not in coordinator.angelegte_kennungen
    ]

    for eintrag in veraltet:
        _LOGGER.info(
            "Entferne nicht mehr vorhandene Entitaet %s", eintrag.entity_id
        )
        registry.async_remove(eintrag.entity_id)

    if veraltet:
        _LOGGER.info(
            "%s veraltete Entitaeten entfernt", len(veraltet)
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entlaedt einen Konfigurationseintrag."""
    coordinator: WattpilotCoordinator = entry.runtime_data
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await coordinator.async_shutdown_connection()
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Laedt einen Konfigurationseintrag neu, wenn sich Einstellungen aendern.

    Das Neuladen wird eingeplant statt sofort ausgefuehrt. Ein Neuladen
    direkt aus dem Listener heraus kann sich sonst selbst blockieren,
    weil der Listener waehrend des Entladens noch laeuft.

    Aeltere Home-Assistant-Fassungen kennen das Einplanen noch nicht.
    Fuer die wird direkt neu geladen.
    """
    einplanen = getattr(hass.config_entries, "async_schedule_reload", None)
    if einplanen is not None:
        einplanen(entry.entry_id)
        return
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
