"""Auswahllisten fuer Parameter mit festen Wertetabellen.

Hier liegen unter anderem der Lademodus, der Force State zum sofortigen
Starten und Stoppen sowie die Phasenumschaltung.
"""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SELECTS
from .entity import WattpilotEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        WattpilotSelect(coordinator, description) for description in SELECTS
    )


class WattpilotSelect(WattpilotEntity, SelectEntity):
    """Eine Auswahlliste fuer genau eine setzbare Property."""

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description)
        self._value_map = description.value_map or {}
        # Rueckwaerts-Zuordnung, um vom Klartext auf den Zahlenwert zu kommen
        self._reverse_map = {v: int(k) for k, v in self._value_map.items()}
        self._attr_options = list(self._value_map.values())

    @property
    def current_option(self) -> str | None:
        value = self.raw_value
        if value is None:
            return None
        return self._value_map.get(str(value))

    async def async_select_option(self, option: str) -> None:
        if option not in self._reverse_map:
            raise ValueError(f"Unbekannte Auswahl: {option}")
        await self.async_write_value(self._reverse_map[option])
