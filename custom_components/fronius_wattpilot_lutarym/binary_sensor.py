"""Binaersensoren fuer lesbare Ja-Nein-Properties."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cards import CardInfo, active_card_index, registered_cards
from .const import (
    BINARY_SENSORS,
    CAR_STATE_CHARGING,
    PROP_CARDS,
    PROP_CAR_STATE,
    WattpilotDescription,
)
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

    # Je benutzter Karte eine Anzeige, ob gerade mit ihr geladen wird.
    # Die laufende Transaktion meldet der Wattpilot erst, wenn zum ersten
    # Mal eine Karte vorgehalten wurde, deshalb wird hier nur die
    # Kartenliste herangezogen.
    for karte in registered_cards(coordinator.data):
        entities.append(WattpilotCardActiveSensor(coordinator, karte))

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


class WattpilotCardActiveSensor(WattpilotEntity, BinarySensorEntity):
    """Zeigt, ob gerade mit dieser RFID-Karte geladen wird.

    Eingeschaltet ist der Sensor, sobald die Karte die laufende
    Transaktion haelt und das Fahrzeug tatsaechlich laedt. Haelt die
    Karte die Transaktion, ohne dass Strom fliesst, steht das in den
    Attributen.
    """

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator, karte: CardInfo) -> None:
        super().__init__(
            coordinator,
            WattpilotDescription(
                key=f"{PROP_CARDS}_{karte.index}_active",
                translation_key="card_active",
                enabled=True,
            ),
        )
        self._index = karte.index
        self._attr_translation_placeholders = {"card": karte.display_name}

    @property
    def _haelt_transaktion(self) -> bool:
        return active_card_index(self.coordinator.data) == self._index

    @property
    def _laedt(self) -> bool:
        status = (self.coordinator.data or {}).get(PROP_CAR_STATE)
        try:
            return int(status) == CAR_STATE_CHARGING
        except (TypeError, ValueError):
            return False

    @property
    def is_on(self) -> bool:
        return self._haelt_transaktion and self._laedt

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        return {
            "card_index": self._index,
            "holds_transaction": self._haelt_transaktion,
        }
