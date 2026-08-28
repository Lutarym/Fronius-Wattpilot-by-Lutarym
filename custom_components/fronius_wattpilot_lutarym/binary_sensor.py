"""Binaersensoren fuer lesbare Ja-Nein-Properties."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SENSORS, PROP_CAR_STATE, WattpilotDescription
from .entity import WattpilotEntity

# Geraeteklassen fuer einzelne Properties
DEVICE_CLASS_BY_KEY = {
    "alw": BinarySensorDeviceClass.RUNNING,
    "cwsc": BinarySensorDeviceClass.CONNECTIVITY,
    "cws": BinarySensorDeviceClass.CONNECTIVITY,
}

# Werte des Fahrzeugstatus, bei denen ein Fahrzeug angesteckt ist.
# 1 heisst laut Bibliothek NO_CAR, 2 laedt, 3 angesteckt und wartet,
# 4 Ladung abgeschlossen.
CAR_CONNECTED_STATES = (2, 3, 4)

CAR_CONNECTED_DESCRIPTION = WattpilotDescription(
    key="car_connected",
    translation_key="car_connected",
    enabled=True,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[BinarySensorEntity] = [
        WattpilotBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if coordinator.is_available(description.key)
    ]

    # Ob ein Fahrzeug angesteckt ist, meldet der Wattpilot nicht direkt.
    # Es ergibt sich aus dem Fahrzeugstatus.
    if coordinator.is_available(PROP_CAR_STATE):
        entities.append(
            WattpilotCarConnectedSensor(coordinator, CAR_CONNECTED_DESCRIPTION)
        )

    async_add_entities(entities)


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


class WattpilotCarConnectedSensor(WattpilotEntity, BinarySensorEntity):
    """Zeigt, ob ein Fahrzeug angesteckt ist.

    Der Wattpilot meldet das nicht als eigenen Wert. Es ergibt sich aus
    dem Fahrzeugstatus.
    """

    _attr_device_class = BinarySensorDeviceClass.PLUG

    @property
    def is_on(self) -> bool | None:
        status = (self.coordinator.data or {}).get(PROP_CAR_STATE)
        if status is None:
            return None
        try:
            return int(status) in CAR_CONNECTED_STATES
        except (TypeError, ValueError):
            return None
