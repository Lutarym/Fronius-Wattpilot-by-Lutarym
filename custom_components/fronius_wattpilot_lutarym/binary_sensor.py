"""Binaersensoren fuer lesbare Ja-Nein-Properties."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SENSORS
from .entity import WattpilotEntity

# Geraeteklassen fuer einzelne Properties
DEVICE_CLASS_BY_KEY = {
    "alw": BinarySensorDeviceClass.RUNNING,
    "cwsc": BinarySensorDeviceClass.CONNECTIVITY,
    "cws": BinarySensorDeviceClass.CONNECTIVITY,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        WattpilotBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if coordinator.is_available(description.key)
    )


class WattpilotBinarySensor(WattpilotEntity, BinarySensorEntity):
    """Ein Binaersensor fuer genau eine Property."""

    def __init__(self, coordinator, description) -> None:
        super().__init__(coordinator, description)
        self._attr_device_class = DEVICE_CLASS_BY_KEY.get(description.key)

    @property
    def is_on(self) -> bool | None:
        value = self.raw_value
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
