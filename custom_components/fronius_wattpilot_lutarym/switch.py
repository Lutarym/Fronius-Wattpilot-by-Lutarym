"""Schalter fuer setzbare Ja-Nein-Parameter."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SWITCHS
from .entity import WattpilotEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        WattpilotSwitch(coordinator, description)
        for description in SWITCHS
        if coordinator.is_available(description.key)
    )


class WattpilotSwitch(WattpilotEntity, SwitchEntity):
    """Ein Schalter fuer genau eine setzbare Property."""

    @property
    def is_on(self) -> bool | None:
        value = self.raw_value
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_write_value(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_write_value(False)
