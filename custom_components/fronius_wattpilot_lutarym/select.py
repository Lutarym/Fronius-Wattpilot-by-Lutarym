"""Auswahllisten fuer Parameter mit festen Wertetabellen.

Hier liegen unter anderem der Lademodus, der Force State zum sofortigen
Starten und Stoppen sowie die Phasenumschaltung.
"""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SELECTS
from .entity import WattpilotEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        WattpilotSelect(coordinator, description)
        for description in SELECTS
        if coordinator.is_available(description.key)
    ])


class WattpilotSelect(WattpilotEntity, SelectEntity):
    """Eine Auswahlliste fuer genau eine setzbare Property."""

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description)
        self._value_map = description.value_map or {}
        # Rueckwaerts-Zuordnung vom Zustandsschluessel auf den Zahlenwert.
        # Die Anzeige der Schluessel uebernimmt Home Assistant anhand der
        # Sprachdateien unter translations/.
        self._reverse_map: dict[str, int] = {}
        for rohwert, zustand in self._value_map.items():
            if zustand in self._reverse_map:
                # Zwei Zahlenwerte auf denselben Zustand: Der Nutzer
                # koennte den zweiten nie auswaehlen. Lieber melden als
                # stillschweigend verschlucken.
                _LOGGER.warning(
                    "Auswahlliste %s: Der Zustand %s steht fuer mehrere "
                    "Werte (%s und %s). Es wird der erste verwendet.",
                    description.key,
                    zustand,
                    self._reverse_map[zustand],
                    rohwert,
                )
                continue
            try:
                self._reverse_map[zustand] = int(rohwert)
            except (TypeError, ValueError):
                _LOGGER.warning(
                    "Auswahlliste %s: Der Wert %r ist keine Zahl und wird "
                    "uebersprungen.",
                    description.key,
                    rohwert,
                )

        self._attr_options = list(self._reverse_map)

    @property
    def current_option(self) -> str | None:
        value = self.raw_value
        if value is None:
            return None
        return self._value_map.get(str(value))

    async def async_select_option(self, option: str) -> None:
        if option not in self._reverse_map:
            raise ServiceValidationError(
                f"{option} ist fuer diese Auswahlliste nicht moeglich."
            )
        await self.async_write_value(self._reverse_map[option])
