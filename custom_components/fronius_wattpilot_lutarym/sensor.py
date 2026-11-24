"""Sensoren fuer alle lesbaren Wattpilot-Properties."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cards import (
    CardInfo,
    active_card_index,
    card_by_index,
    charging_without_card,
    registered_cards,
    session_energy,
    transaction,
)
from .const import (
    CARD_ENERGY_UNIT,
    PROP_CARDS,
    SENSORS,
    WattpilotDescription,
)
from .entity import WattpilotEntity

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASSES = {
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "frequency": SensorDeviceClass.FREQUENCY,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "signal_strength": SensorDeviceClass.SIGNAL_STRENGTH,
    "data_size": SensorDeviceClass.DATA_SIZE,
    "battery": SensorDeviceClass.BATTERY,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
    "duration": SensorDeviceClass.DURATION,
    "timestamp": SensorDeviceClass.TIMESTAMP,
    "monetary": SensorDeviceClass.MONETARY,
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
        WattpilotSensor(coordinator, description)
        for description in SENSORS
        if coordinator.is_available(description.key)
    ]

    # Je benutzter RFID-Karte ein Satz Entitaeten, damit die Ladungen
    # dem jeweiligen Fahrzeug zugeordnet sind.
    #
    # Massgeblich ist allein, ob die Kartenliste Karten enthaelt. Die
    # Verfuegbarkeitspruefung wird hier bewusst nicht befragt: Werte wie
    # die laufende Transaktion meldet der Wattpilot erst, wenn zum
    # ersten Mal eine Karte vorgehalten wurde.
    karten = registered_cards(coordinator.data)
    for karte in karten:
        entities.append(WattpilotCardEnergySensor(coordinator, karte))
        entities.append(WattpilotCardSessionSensor(coordinator, karte))

    if karten:
        entities.append(WattpilotActiveCardSensor(coordinator))
        _LOGGER.debug(
            "Benutzte RFID-Karten: %s",
            ", ".join(f"{k.index + 1}: {k.display_name}" for k in karten),
        )
    else:
        _LOGGER.debug(
            "Keine benutzte RFID-Karte gefunden. Gemeldete Kartenliste: %s",
            (coordinator.data or {}).get(PROP_CARDS, "nicht gemeldet"),
        )

    _LOGGER.debug(
        "%s Sensoren angelegt, davon %s aus der Eigenschaftstabelle",
        len(entities),
        len(SENSORS),
    )
    async_add_entities(entities)


class WattpilotSensor(WattpilotEntity, SensorEntity):
    """Ein Sensor fuer genau eine Property."""

    # Zusammengesetzte Werte wie die Kartenliste, die Preisliste oder
    # die Liste gefundener WLAN-Netze landen vollstaendig in den
    # Attributen. Die gehoeren nicht in die Verlaufsdatenbank, sie
    # wuerden sie bei jeder Aktualisierung unnoetig aufblaehen.
    _unrecorded_attributes = frozenset({MATCH_ALL})

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

        # Zahlenwert in den uebersetzten Zustand umsetzen.
        #
        # Ein Wert, der nicht in der Tabelle steht, ergibt bewusst
        # "unbekannt". Home Assistant prueft bei Auswahl-Sensoren, ob
        # der Zustand in der Liste der moeglichen Werte steht, und
        # schriebe sonst bei jeder Aktualisierung einen Fehler ins
        # Protokoll. Der Rohwert steht in den Attributen.
        if description.value_map:
            return description.value_map.get(str(value))

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

        # Nicht zugeordneter Wert einer Auswahlliste: Der Zustand bleibt
        # unbekannt, damit Home Assistant nicht meckert. Damit die
        # Angabe nicht verloren geht, steht sie hier.
        beschreibung = self.entity_description_data
        if beschreibung.value_map and value is not None:
            if str(value) not in beschreibung.value_map:
                return {"unbekannter_rohwert": value}
            return None

        if isinstance(value, dict):
            return {str(k): v for k, v in value.items()}
        if isinstance(value, list):
            return {"items": value}
        return None


class WattpilotCardEntity(WattpilotEntity, SensorEntity):
    """Basis fuer Sensoren, die sich auf eine einzelne RFID-Karte beziehen.

    Der Anzeigename traegt den Kartennamen, damit die Werte unmittelbar
    dem Fahrzeug zugeordnet sind. Die eindeutige Kennung richtet sich
    dagegen nach dem Kartenindex, damit ein Umbenennen in der App den
    bisherigen Verlauf nicht abschneidet.
    """

    def __init__(
        self,
        coordinator,
        karte: CardInfo,
        suffix: str,
        translation_key: str,
    ) -> None:
        description = WattpilotDescription(
            key=f"{PROP_CARDS}_{karte.index}_{suffix}",
            translation_key=translation_key,
            enabled=True,
        )
        super().__init__(coordinator, description)
        self._index = karte.index
        self._attr_translation_placeholders = {"card": karte.display_name}

    @property
    def card(self) -> CardInfo | None:
        return card_by_index(self.coordinator.data, self._index)

    @property
    def ist_aktiv(self) -> bool:
        """Ob gerade mit dieser Karte geladen wird."""
        return active_card_index(self.coordinator.data) == self._index


class WattpilotCardEnergySensor(WattpilotCardEntity):
    """Gesamte Energie, die ueber diese Karte geladen wurde.

    Dieser Zaehler wird vom Wattpilot selbst gefuehrt und laeuft ueber
    alle Ladungen hinweg weiter. Er eignet sich fuer das
    Energie-Dashboard, um den Verbrauch je Fahrzeug zu erfassen.
    """

    _attr_native_unit_of_measurement = CARD_ENERGY_UNIT
    _attr_device_class = SensorDeviceClass.ENERGY
    # Bewusst total und nicht total_increasing: Der Zaehler laesst sich
    # in der Wattpilot-App zuruecksetzen, und die uebrigen Energiewerte
    # dieser Schnittstelle sind aus demselben Grund ebenfalls total.
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, karte: CardInfo) -> None:
        super().__init__(coordinator, karte, "energy", "card_energy_total")

    @property
    def native_value(self) -> float | None:
        karte = self.card
        return karte.energy if karte else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        karte = self.card
        return {
            "card_index": self._index,
            "card_name": karte.display_name if karte else None,
            "card_registered": karte.registered if karte else None,
            "active": self.ist_aktiv,
        }


class WattpilotCardSessionSensor(WattpilotCardEntity, RestoreSensor):
    """Energie der laufenden oder zuletzt mit dieser Karte gefahrenen Ladung.

    Der Wattpilot fuehrt keinen solchen Zaehler je Karte. Er meldet nur
    die Energie seit dem Anstecken des Fahrzeugs. Diese Entitaet merkt
    sich diesen Wert, solange die Karte die laufende Transaktion haelt,
    und behaelt ihn danach bei. So bleibt nach dem Abstecken sichtbar,
    wie viel das Fahrzeug zuletzt geladen hat.

    Der Wert bekommt bewusst keine Zustandsklasse: Er faellt beim Beginn
    einer neuen Ladung auf null zurueck und taugt deshalb nicht als
    Zaehlerstand fuer die Langzeitstatistik. Dafuer ist der
    Gesamtzaehler der Karte da.
    """

    _attr_native_unit_of_measurement = CARD_ENERGY_UNIT
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(self, coordinator, karte: CardInfo) -> None:
        super().__init__(coordinator, karte, "session", "card_energy_session")
        self._wert: float | None = None

    async def async_added_to_hass(self) -> None:
        """Den zuletzt gemerkten Wert nach einem Neustart wiederherstellen."""
        await super().async_added_to_hass()
        letzter = await self.async_get_last_sensor_data()
        if letzter is not None and letzter.native_value is not None:
            try:
                self._wert = float(letzter.native_value)
            except (TypeError, ValueError):
                self._wert = None
        self._uebernehmen()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._uebernehmen()
        super()._handle_coordinator_update()

    def _uebernehmen(self) -> None:
        """Den aktuellen Ladewert uebernehmen, solange die Karte aktiv ist."""
        self._wert = session_energy(
            self._wert, self.coordinator.data, self._index
        )

    @property
    def native_value(self) -> float | None:
        return self._wert

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "card_index": self._index,
            "running": self.ist_aktiv,
        }


class WattpilotActiveCardSensor(WattpilotEntity, SensorEntity):
    """Name der Karte, die gerade vorgehalten wurde.

    Laeuft keine Transaktion oder wird ohne Karte geladen, bleibt der
    Wert leer. Die Einzelheiten stehen dann in den Attributen.
    """

    def __init__(self, coordinator) -> None:
        super().__init__(
            coordinator,
            WattpilotDescription(
                key="active_card",
                translation_key="active_card",
                enabled=True,
            ),
        )

    @property
    def native_value(self) -> str | None:
        index = active_card_index(self.coordinator.data)
        if index is None:
            return None
        karte = card_by_index(self.coordinator.data, index)
        return karte.display_name if karte else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        daten = self.coordinator.data
        return {
            "card_index": active_card_index(daten),
            "without_card": charging_without_card(daten),
            "transaction": transaction(daten),
        }
