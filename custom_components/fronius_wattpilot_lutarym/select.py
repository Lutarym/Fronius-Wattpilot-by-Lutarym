from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from wattpilot_api import LoadMode

from .entity import WattpilotEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    async_add_entities([WattpilotModeSelect(entry.runtime_data)])


class WattpilotModeSelect(WattpilotEntity, SelectEntity):
    _attr_name = "Charging mode"
    _attr_unique_id = "wattpilot_charging_mode"

    @property
    def options(self):
        return [mode.name for mode in LoadMode]

    @property
    def current_option(self):
        value = self.value("mode")
        if value is None:
            return None
        try:
            return LoadMode(value).name
        except (ValueError, TypeError):
            return str(value)

    async def async_select_option(self, option: str):
        await self.coordinator.api.set_mode(LoadMode[option])
