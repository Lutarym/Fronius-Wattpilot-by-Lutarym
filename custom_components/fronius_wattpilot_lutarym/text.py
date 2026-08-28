"""Text-Eingaben fuer setzbare Zeichenketten."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import TEXTS
from .entity import WattpilotEntity

# Hoechstlaengen laut API-Definition
MAX_LENGTH_BY_KEY = {
    "ct": 64,
    "fna": 64,
    "log": 64,
    "wan": 32,
}

# Farbwerte im Format #RRGGBB
COLOR_KEYS = {"cch", "cfi", "cid", "cwc"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        WattpilotText(coordinator, description)
        for description in TEXTS
        if coordinator.is_available(description.key)
    ])


class WattpilotText(WattpilotEntity, TextEntity):
    """Eine Text-Eingabe fuer genau eine setzbare Property."""

    _attr_mode = TextMode.TEXT

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description)
        self._attr_native_max = MAX_LENGTH_BY_KEY.get(description.key, 255)
        if description.key in COLOR_KEYS:
            self._attr_pattern = r"^#[0-9A-Fa-f]{6}$"

    @property
    def native_value(self) -> str | None:
        value = self.raw_value
        return str(value) if value is not None else None

    async def async_set_value(self, value: str) -> None:
        await self.coordinator.async_set_property(
            self.entity_description_data.key, value
        )
