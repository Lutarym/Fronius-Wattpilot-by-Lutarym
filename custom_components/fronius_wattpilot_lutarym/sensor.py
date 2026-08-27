"""Sensoren fuer alle lesbaren Wattpilot-Properties."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    MAX_RFID_CARDS,
    PROP_CARDS,
    SENSORS,
    WattpilotDescription,
)
from .entity import WattpilotEntity

DEVICE_CLASSES = {
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "frequency": SensorDeviceClass.FREQUENCY,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "signal_strength": SensorDeviceClass.SIGNAL_STRENGTH,
    "data_size": SensorDeviceClass.DATA_SIZE,
}

STATE_CLASSES = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total": SensorStateClass.TOTAL,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
}

# Laengster erlaubter Zustandswert in Home Assistant
MAX_STATE_LENGTH = 255


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        WattpilotSensor(coordinator, description) for description in SENSORS
    ]

    # Fuer jede registrierte RFID-Karte einen eigenen Energiezaehler anlegen.
    cards = (coordinator.data or {}).get(PROP_CARDS)
    if isinstance(cards, list):
        for index in range(min(len(cards), MAX_RFID_CARDS)):
            entities.append(WattpilotCardEnergySensor(coordinator, index))
            entities.append(WattpilotCardNameSensor(coordinator, index))

    async_add_entities(entities)


class WattpilotSensor(WattpilotEntity, SensorEntity):
    """Ein Sensor fuer genau eine Property."""

    def __init__(self, coordinator, description: WattpilotDescription) -> None:
        super().__init__(coordinator, description)
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = DEVICE_CLASSES.get(description.device_class or "")
        self._attr_state_class = STATE_CLASSES.get(description.state_class or "")

        # Werte mit Klartext-Zuordnung sind Auswahllisten, keine Messwerte.
        if description.value_map:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(description.value_map.values())
            self._attr_state_class = None
            self._attr_native_unit_of_measurement = None

    @property
    def native_value(self) -> Any:
        value = self.raw_value
        if value is None:
            return None

        description = self.entity_description_data

        # Zahlenwert in Klartext uebersetzen
        if description.value_map:
            return description.value_map.get(str(value), str(value))

        # Zusammengesetzte Werte als Text darstellen, Details in den Attributen
        if isinstance(value, (list, dict)):
            return len(value)

        if isinstance(value, bool):
            return str(value)

        if isinstance(value, (int, float)):
            return value

        text = str(value)
        return text[:MAX_STATE_LENGTH] if len(text) > MAX_STATE_LENGTH else text

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Bei zusammengesetzten Werten den vollstaendigen Inhalt bereitstellen."""
        value = self.raw_value
        if isinstance(value, dict):
            return {str(k): v for k, v in value.items()}
        if isinstance(value, list):
            return {"items": value}
        return None


class WattpilotCardEntity(WattpilotEntity, SensorEntity):
    """Basis fuer Sensoren, die sich auf eine einzelne RFID-Karte beziehen."""

    def __init__(self, coordinator, index: int, suffix: str, label: str) -> None:
        description = WattpilotDescription(
            key=f"{PROP_CARDS}_{index}_{suffix}",
            name=f"RFID-Karte {index + 1} {label}",
            enabled=True,
        )
        super().__init__(coordinator, description)
        self._index = index

    @property
    def card(self) -> dict[str, Any] | None:
        cards = (self.coordinator.data or {}).get(PROP_CARDS)
        if isinstance(cards, list) and self._index < len(cards):
            entry = cards[self._index]
            if isinstance(entry, dict):
                return entry
        return None


class WattpilotCardEnergySensor(WattpilotCardEntity):
    """Energiezaehler einer einzelnen RFID-Karte."""

    _attr_native_unit_of_measurement = "Wh"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, index: int) -> None:
        super().__init__(coordinator, index, "energy", "Energie")

    @property
    def native_value(self) -> float | None:
        card = self.card
        if not card:
            return None
        value = card.get("energy")
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None


class WattpilotCardNameSensor(WattpilotCardEntity):
    """Name einer einzelnen RFID-Karte."""

    def __init__(self, coordinator, index: int) -> None:
        super().__init__(coordinator, index, "name", "Name")

    @property
    def native_value(self) -> str | None:
        card = self.card
        if not card:
            return None
        name = card.get("name")
        return str(name) if name is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        card = self.card
        if not card:
            return None
        return {"card_registered": card.get("cardId")}
