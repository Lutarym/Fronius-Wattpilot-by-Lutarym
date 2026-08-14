from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import WattpilotAPI
from .const import DOMAIN
from .coordinator import WattpilotCoordinator

PLATFORMS = ["sensor", "binary_sensor", "number", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = WattpilotAPI(entry.data["host"], entry.data["password"])
    coordinator = WattpilotCoordinator(hass, api)
    await coordinator.async_connect()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: WattpilotCoordinator = entry.runtime_data
    await coordinator.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
