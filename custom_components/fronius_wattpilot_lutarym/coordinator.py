"""Verwaltet die dauerhafte WebSocket-Verbindung zum Wattpilot."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from wattpilot_api.exceptions import AuthenticationError

from .api import WattpilotAPI
from .cards import parse_cards
from .const import DEFAULT_ONLY_AVAILABLE, OPT_ONLY_AVAILABLE

_LOGGER = logging.getLogger(__name__)

# Abstand, in dem geprueft wird, ob die Verbindung noch steht
WATCHDOG_INTERVAL = timedelta(seconds=60)

# Wartezeit zwischen Wiederverbindungsversuchen, waechst bis zum Hoechstwert
RECONNECT_DELAY = 10
RECONNECT_DELAY_MAX = 300

# Sammelphase beim Verbindungsaufbau.
#
# Der Wattpilot schickt seinen Vollstatus in mehreren Teilnachrichten. Die
# Bibliothek meldet die Verbindung aber schon als fertig, sobald irgendeine
# Aenderungsnachricht eintrifft, auch wenn die Teilnachrichten noch laufen.
# Deshalb wird hier gewartet, bis sich der Satz der gemeldeten Schluessel
# ueber mehrere Durchlaeufe hinweg nicht mehr veraendert. Eine einzelne
# ruhige Runde genuegt nicht: Eine verspaetete Teilnachricht wuerde sonst
# verpasst, und die darin enthaltenen Werte bekaemen keine Entitaet.
SETTLE_STEP = 0.5
SETTLE_STABLE_ROUNDS = 4
SETTLE_TIMEOUT = 20.0


class WattpilotCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Haelt die Verbindung offen und verteilt eingehende Werte."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WattpilotAPI,
        entry: ConfigEntry,
    ) -> None:
        self.api = api
        self.entry = entry
        self.connected = False
        # Die Schluessel, die dieses Geraet tatsaechlich liefert.
        # Wird beim Verbindungsaufbau einmal ermittelt.
        self.available_keys: set[str] = set()
        # Kennungen aller Entitaeten, die tatsaechlich angelegt wurden.
        # Wird beim Aufraeumen des Registers gebraucht.
        self.angelegte_kennungen: set[str] = set()
        # Erst wenn die Entitaeten stehen, darf auf eine geaenderte
        # Kartenliste mit einem Neuladen reagiert werden.
        self.setup_abgeschlossen = False
        self._karten_signatur: tuple | None = None
        self._reconnect_task: asyncio.Task | None = None
        self._reconnect_delay = RECONNECT_DELAY
        # Abmeldefunktion des Rueckrufs, damit sich bei einer
        # Wiederverbindung keine Rueckrufe ansammeln.
        self._abmelden: Callable[[], None] | None = None
        # Aenderungen werden gesammelt und einmal je Nachricht verarbeitet.
        self._uebernahme_geplant = False
        self._beendet = False
        # Zuletzt gesehener Satz roher Schluessel, fuer die billige
        # Vorpruefung in _merke_neue_schluessel.
        self._bekannte_rohschluessel: set[str] = set()
        super().__init__(
            hass,
            _LOGGER,
            name="Fronius Wattpilot by Lutarym",
            # Die Werte kommen per Push. Der Zyklus dient nur der
            # Ueberwachung, ob die Verbindung noch steht.
            update_interval=WATCHDOG_INTERVAL,
        )

    def is_available(self, key: str) -> bool:
        """Liefert, ob eine Property auf diesem Geraet vorhanden ist."""
        if not self.filter_entities:
            return True
        # Sicherheitsnetz: Hat die Erkennung nichts geliefert, werden alle
        # Entitaeten angelegt. Ein Geraet ohne jede Entitaet waere unbrauchbar.
        if not self.available_keys:
            return True
        return key in self.available_keys

    @property
    def filter_entities(self) -> bool:
        """Ob nur vorhandene Properties als Entitaet angelegt werden."""
        return self.entry.options.get(OPT_ONLY_AVAILABLE, DEFAULT_ONLY_AVAILABLE)

    async def _async_update_data(self) -> dict[str, Any]:
        """Wird vom Ueberwachungszyklus aufgerufen."""
        if not self.api.connected:
            self.connected = False
            self._schedule_reconnect()
            return self.data or {}

        self.connected = True
        return self.api.properties()

    async def async_connect(self) -> None:
        """Baut die erste Verbindung auf und ermittelt die vorhandenen Werte."""
        try:
            await self.api.connect()
        except AuthenticationError as err:
            # Home Assistant fragt daraufhin selbst nach dem Passwort.
            # Ein erneuter Verbindungsversuch waere zwecklos.
            self.connected = False
            raise ConfigEntryAuthFailed(
                f"Der Wattpilot hat das Passwort abgelehnt: {err}"
            ) from err
        except Exception as err:  # noqa: BLE001
            self.connected = False
            raise ConfigEntryNotReady(
                f"Verbindung zum Wattpilot nicht moeglich: {err}"
            ) from err

        self.connected = True
        self._reconnect_delay = RECONNECT_DELAY

        # Das Geraet meldet seinen Zustand teilweise in mehreren Nachrichten.
        # Die Bibliothek betrachtet die Verbindung schon nach der ersten
        # Nachricht als fertig. Deshalb wird hier kurz gewartet, damit auch
        # nachfolgende Teilmeldungen ankommen, bevor entschieden wird,
        # welche Entitaeten angelegt werden.
        await self._async_wait_for_properties()

        self.available_keys = self.api.available_keys()
        if self.available_keys:
            _LOGGER.debug(
                "Wattpilot meldet %s Properties: %s",
                len(self.available_keys),
                ", ".join(sorted(self.available_keys)),
            )
        else:
            _LOGGER.warning(
                "Der Wattpilot hat keine Properties gemeldet. Es werden "
                "vorsorglich alle Entitaeten angelegt."
            )

        self._subscribe()
        self.async_set_updated_data(self.api.properties())

    async def _async_wait_for_properties(self) -> None:
        """Wartet, bis der Wattpilot alle Teilnachrichten geschickt hat.

        Beendet wird erst, wenn sich der Satz der gemeldeten Schluessel
        ueber SETTLE_STABLE_ROUNDS Durchlaeufe hinweg nicht mehr
        veraendert hat. Verglichen werden die Schluessel selbst und nicht
        nur ihre Anzahl, denn eine Teilnachricht kann einen Schluessel
        ersetzen, ohne die Anzahl zu veraendern.

        Spaetestens nach SETTLE_TIMEOUT wird abgebrochen, damit die
        Einrichtung bei einem stillen Geraet nicht haengen bleibt.
        """
        bekannt: set[str] = set()
        ruhige_runden = 0
        gewartet = 0.0

        while gewartet < SETTLE_TIMEOUT:
            await asyncio.sleep(SETTLE_STEP)
            gewartet += SETTLE_STEP

            aktuell = set(self.api.raw_properties())
            if aktuell and aktuell == bekannt:
                ruhige_runden += 1
                if ruhige_runden >= SETTLE_STABLE_ROUNDS:
                    _LOGGER.debug(
                        "Sammelphase nach %.1f Sekunden beendet, "
                        "%s Properties gemeldet",
                        gewartet,
                        len(aktuell),
                    )
                    return
                continue

            if aktuell != bekannt:
                neue = aktuell - bekannt
                if bekannt and neue:
                    _LOGGER.debug(
                        "Nachzuegler nach %.1f Sekunden: %s",
                        gewartet,
                        ", ".join(sorted(neue)),
                    )
                bekannt = aktuell
                ruhige_runden = 0

        _LOGGER.warning(
            "Der Wattpilot hat auch nach %s Sekunden noch keinen "
            "stabilen Zustand gemeldet. Es wird mit %s Properties "
            "weitergemacht.",
            SETTLE_TIMEOUT,
            len(bekannt),
        )

    def _subscribe(self) -> None:
        """Meldet den Coordinator fuer Wertaenderungen an.

        Die Bibliothek ruft den Rueckruf einmal je geaenderter Property
        auf. Eine einzige Statusnachricht des Wattpilot kann mehrere
        hundert Properties enthalten. Wuerde hier jedes Mal sofort
        aktualisiert, schriebe jede Entitaet bei einer Nachricht
        hundertfach ihren Zustand neu.

        Deshalb wird die Verarbeitung nur vorgemerkt und einmal am Ende
        des laufenden Durchlaufs erledigt. Da alle Rueckrufe einer
        Nachricht nacheinander im selben Durchlauf feuern, wird so aus
        einer Nachricht genau eine Aktualisierung, ohne Verzoegerung.
        """
        self._rueckruf_abmelden()

        @callback
        def property_changed(name: str, value: Any) -> None:
            if self._beendet or self._uebernahme_geplant:
                return
            self._uebernahme_geplant = True
            self.hass.loop.call_soon(self._uebernehmen)

        self._abmelden = self.api.subscribe(property_changed)

    @callback
    def _rueckruf_abmelden(self) -> None:
        """Meldet einen zuvor angemeldeten Rueckruf wieder ab.

        Scheitern darf das nie: Beim Wiederverbinden gehoert die
        Abmeldefunktion zu einem Client, den es moeglicherweise schon
        nicht mehr gibt.
        """
        if self._abmelden is None:
            return
        try:
            self._abmelden()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Rueckruf liess sich nicht abmelden: %s", err)
        finally:
            self._abmelden = None

    @callback
    def _uebernehmen(self) -> None:
        """Verarbeitet die gesammelten Aenderungen einer Statusnachricht."""
        self._uebernahme_geplant = False
        if self._beendet:
            return

        daten = self.api.properties()
        self.async_set_updated_data(daten)
        self._merke_neue_schluessel()
        self._pruefe_kartenwechsel(daten)

    @callback
    def _merke_neue_schluessel(self) -> None:
        """Nimmt spaeter eintreffende Schluessel in die Liste auf.

        Meldet der Wattpilot einen Wert erst nach der Sammelphase, zum
        Beispiel weil eine Funktion gerade erst eingeschaltet wurde,
        gilt er von da an als vorhanden. Damit wird er beim naechsten
        Einrichten nicht mehr aussortiert und seine Entitaet bleibt beim
        Aufraeumen des Registers verschont.
        """
        if not self.available_keys:
            return

        # Erst die billige Pruefung: Hat das Geraet ueberhaupt einen
        # neuen Schluessel gemeldet? Nur dann lohnt sich das Aufloesen
        # der zusammengesetzten Werte.
        roh = set(self.api.raw_properties())
        if roh == self._bekannte_rohschluessel:
            return
        self._bekannte_rohschluessel = roh

        neue = self.api.available_keys() - self.available_keys
        if neue:
            self.available_keys |= neue
            _LOGGER.debug(
                "Nachtraeglich gemeldete Properties: %s", ", ".join(sorted(neue))
            )

    @staticmethod
    def _karten_signatur_aus(daten: dict[str, Any] | None) -> tuple:
        """Kennzeichnet die Kartenliste nach Anzahl, Index und Name.

        Der Energiezaehler gehoert bewusst nicht dazu, der aendert sich
        waehrend jeder Ladung.
        """
        return tuple(
            (karte.index, karte.name, karte.registered)
            for karte in parse_cards(daten)
        )

    @callback
    def _pruefe_kartenwechsel(self, daten: dict[str, Any] | None) -> None:
        """Laedt neu, wenn eine Karte angelernt, umbenannt oder entfernt wurde.

        Die Entitaeten einer Karte entstehen beim Einrichten. Kommt
        spaeter eine Karte hinzu, muss die Integration neu geladen
        werden, damit sie ihre Entitaeten bekommt.
        """
        if not self.setup_abgeschlossen:
            return

        neu = self._karten_signatur_aus(daten)
        if self._karten_signatur is None:
            self._karten_signatur = neu
            return
        if neu == self._karten_signatur:
            return

        # Sofort merken, sonst loesen die naechsten Meldungen noch
        # einmal dasselbe Neuladen aus.
        self._karten_signatur = neu
        self.setup_abgeschlossen = False
        _LOGGER.info(
            "Die Kartenliste hat sich geaendert, die Integration wird neu geladen"
        )
        einplanen = getattr(
            self.hass.config_entries, "async_schedule_reload", None
        )
        if einplanen is not None:
            einplanen(self.entry.entry_id)
        else:
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self.entry.entry_id)
            )

    @callback
    def markiere_setup_abgeschlossen(self) -> None:
        """Wird aufgerufen, sobald alle Entitaeten stehen."""
        self._karten_signatur = self._karten_signatur_aus(self.data)
        self.setup_abgeschlossen = True

    def _schedule_reconnect(self) -> None:
        """Startet einen Wiederverbindungsversuch im Hintergrund."""
        if self._reconnect_task and not self._reconnect_task.done():
            return
        self._reconnect_task = self.entry.async_create_background_task(
            self.hass,
            self._reconnect_loop(),
            name="wattpilot_reconnect",
        )

    async def _reconnect_loop(self) -> None:
        """Versucht die Verbindung wiederherzustellen, mit wachsender Pause."""
        while not self.api.connected:
            _LOGGER.warning(
                "Verbindung zum Wattpilot verloren, neuer Versuch in %s Sekunden",
                self._reconnect_delay,
            )
            await asyncio.sleep(self._reconnect_delay)
            try:
                await self.api.disconnect()
                await self.api.connect()
            except AuthenticationError as err:
                # Erneute Versuche sind zwecklos. Home Assistant wird
                # gebeten, nach dem Passwort zu fragen.
                _LOGGER.error(
                    "Der Wattpilot lehnt das gespeicherte Passwort ab: %s", err
                )
                self.entry.async_start_reauth(self.hass)
                return
            except Exception as err:  # noqa: BLE001
                self._reconnect_delay = min(
                    self._reconnect_delay * 2, RECONNECT_DELAY_MAX
                )
                _LOGGER.debug("Wiederverbindung fehlgeschlagen: %s", err)
                continue

            self.connected = True
            self._reconnect_delay = RECONNECT_DELAY
            self._subscribe()
            self.async_set_updated_data(self.api.properties())
            _LOGGER.info("Verbindung zum Wattpilot wiederhergestellt")
            return

    async def async_set_property(self, key: str, value: Any) -> None:
        """Setzt eine Property und uebernimmt den Wert sofort in die Anzeige."""
        await self.api.set_property(key, value)
        data = dict(self.data or {})
        data[key] = value
        self.async_set_updated_data(data)

    async def async_shutdown_connection(self) -> None:
        """Beendet die Verbindung beim Entladen der Integration."""
        self._beendet = True
        self.connected = False
        self._rueckruf_abmelden()
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
        await self.api.disconnect()
