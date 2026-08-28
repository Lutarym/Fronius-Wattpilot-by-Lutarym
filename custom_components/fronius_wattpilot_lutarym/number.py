"""Zahlen-Eingaben fuer setzbare numerische Parameter."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import NUMBERS
from .entity import WattpilotEntity

# Diese Parameter erwartet das Geraet als Ganzzahl
INTEGER_KEYS = {
    "amp", "ama", "mca", "lot", "lof", "lbr", "lop", "trx",
    "fmt", "mci", "mcpd", "psmd", "mptwt", "mpwst", "sumd", "tof", "fot",
}

# Diese Parameter werden als Schieberegler dargestellt
SLIDER_KEYS = {"amp", "ama", "mca", "lbr", "lop", "fam"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        WattpilotNumber(coordinator, description)
        for description in NUMBERS
        if coordinator.is_available(description.key)
    ])


class WattpilotNumber(WattpilotEntity, NumberEntity):
    """Eine Zahlen-Eingabe fuer genau eine setzbare Property."""

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description)
        minimum, maximum, step = description.range
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = description.unit
        self._attr_mode = (
            NumberMode.SLIDER
            if description.key in SLIDER_KEYS
            else NumberMode.BOX
        )

    @property
    def native_value(self) -> float | None:
        value = self.raw_value
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        key = self.entity_description_data.key
        await self.async_write_value(int(value) if key in INTEGER_KEYS else value)
