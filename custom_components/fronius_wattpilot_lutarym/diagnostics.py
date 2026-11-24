"""Diagnosedaten zum Herunterladen.

Zeigt, welche Werte der Wattpilot tatsaechlich meldet und wie die
Integration sie auswertet. Damit laesst sich nachvollziehen, warum eine
Entitaet angelegt wurde oder eben nicht.

Abrufbar unter Einstellungen, Geraete und Dienste, beim Geraet ueber
die Schaltflaeche zum Herunterladen der Diagnose.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .cards import (
    active_card_index,
    charging_without_card,
    parse_cards,
    registered_cards,
    transaction,
)
from .const import (
    BINARY_SENSORS,
    CONF_HOST,
    NUMBERS,
    SELECTS,
    SENSORS,
    SWITCHS,
    TEXTS,
)
from .coordinator import WattpilotCoordinator

# Diese Werte werden nicht mit ausgegeben. Es sind Zugangsdaten
# beziehungsweise Angaben, die das Geraet im Netz auffindbar machen.
GEHEIM = {
    "cak",
    "wak",
    "facwak",
    "gmk",
    "wifis",
    "wss",
    "wcb",
    "wfb",
    "wpb",
    "host",
    "sse",
    "ccw",
    "scan",
}

PLATTFORMEN = {
    "sensor": SENSORS,
    "binary_sensor": BINARY_SENSORS,
    "number": NUMBERS,
    "select": SELECTS,
    "switch": SWITCHS,
    "text": TEXTS,
}


def _saeubern(daten: dict[str, Any]) -> dict[str, Any]:
    """Ersetzt Zugangsdaten durch einen Platzhalter."""
    return {
        schluessel: ("**entfernt**" if schluessel in GEHEIM else wert)
        for schluessel, wert in sorted(daten.items())
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Stellt die Diagnosedaten zusammen."""
    coordinator: WattpilotCoordinator = entry.runtime_data
    roh = coordinator.api.raw_properties()
    aufgeloest = coordinator.data or {}
    verfuegbar = coordinator.available_keys

    # Welche Eintraege der Tabelle mangels Meldung uebersprungen wurden
    uebersprungen: dict[str, list[str]] = {}
    for name, eintraege in PLATTFORMEN.items():
        fehlend = sorted(
            d.key for d in eintraege if not coordinator.is_available(d.key)
        )
        if fehlend:
            uebersprungen[name] = fehlend

    karten = parse_cards(aufgeloest)
    benutzt = registered_cards(aufgeloest)

    return {
        "integration": {
            "verbunden": coordinator.connected,
            "nur_vorhandene_entitaeten": coordinator.filter_entities,
            "setup_abgeschlossen": coordinator.setup_abgeschlossen,
            "angelegte_entitaeten": len(coordinator.angelegte_kennungen),
        },
        "geraet": {
            "firmware": coordinator.api.firmware,
            "modell": coordinator.api.model,
            "adresse_gesetzt": bool(entry.data.get(CONF_HOST)),
        },
        "properties": {
            "anzahl_gemeldet": len(roh),
            "anzahl_mit_untereintraegen": len(aufgeloest),
            "anzahl_als_vorhanden_erkannt": len(verfuegbar),
            "gemeldete_schluessel": sorted(roh),
            "werte": _saeubern(aufgeloest),
        },
        "rfid": {
            "kartenliste_gemeldet": "cards" in roh,
            "eintraege_gesamt": len(karten),
            "benutzte_karten": [
                {
                    "index": k.index,
                    "name": k.name,
                    "anzeigename": k.display_name,
                    "energie": k.energy,
                    "kennung_hinterlegt": k.registered,
                }
                for k in benutzt
            ],
            "alle_eintraege": [
                {
                    "index": k.index,
                    "name": k.name,
                    "energie": k.energy,
                    "kennung_hinterlegt": k.registered,
                }
                for k in karten
            ],
            "transaktion_roh": transaction(aufgeloest),
            "aktiver_kartenindex": active_card_index(aufgeloest),
            "laedt_ohne_karte": charging_without_card(aufgeloest),
            # Zugangssteuerung: 0 heisst offen, 1 heisst Freigabe abwarten
            "zugangsfreigabe_acs": aufgeloest.get("acs"),
            # In der API-Definition ohne Titel und Beschreibung, deshalb
            # ohne eigene Entitaet. Hier zur Beobachtung mit ausgegeben.
            "rfide": aufgeloest.get("rfide"),
        },
        "uebersprungene_entitaeten": uebersprungen,
    }
