"""Verwaltet die dauerhafte WebSocket-Verbindung zum Wattpilot."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import WattpilotAPI
from .const import DEFAULT_ONLY_AVAILABLE, OPT_ONLY_AVAILABLE

_LOGGER = logging.getLogger(__name__)

# Abstand, in dem geprueft wird, ob die Verbindung noch steht
WATCHDOG_INTERVAL = timedelta(seconds=60)

# Wartezeit zwischen Wiederverbindungsversuchen, waechst bis zum Hoechstwert
RECONNECT_DELAY = 10
RECONNECT_DELAY_MAX = 300

# Sammelphase beim Verbindungsaufbau: Es wird so lange gewartet, bis keine
# neuen Properties mehr eintreffen, hoechstens aber SETTLE_TIMEOUT Sekunden.
SETTLE_STEP = 0.5
SETTLE_TIMEOUT = 8.0


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
        self._reconnect_task: asyncio.Task | None = None
        self._reconnect_delay = RECONNECT_DELAY
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
        """Wartet, bis keine neuen Properties mehr eintreffen.

        Bricht spaetestens nach SETTLE_TIMEOUT ab, damit die Einrichtung
        auch bei einem stillen Geraet nicht haengen bleibt.
        """
        anzahl = -1
        gewartet = 0.0

        while gewartet < SETTLE_TIMEOUT:
            neu = len(self.api.raw_properties())
            if neu == anzahl and neu > 0:
                # Seit dem letzten Durchlauf kam nichts Neues hinzu
                return
            anzahl = neu
            await asyncio.sleep(SETTLE_STEP)
            gewartet += SETTLE_STEP

        _LOGGER.debug(
            "Sammelphase nach %s Sekunden beendet, %s Properties bekannt",
            SETTLE_TIMEOUT,
            anzahl,
        )

    def _subscribe(self) -> None:
        """Meldet den Coordinator fuer Wertaenderungen an."""

        @callback
        def property_changed(name: str, value: Any) -> None:
            """Wird bei jeder Wertaenderung vom Geraet aufgerufen."""
            # Die Unter-Werte werden neu aufgeloest, damit zum Beispiel
            # eine Aenderung am Array nrg auch die Einzelwerte aktualisiert.
            self.async_set_updated_data(self.api.properties())

        self.api.subscribe(property_changed)

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
        self.connected = False
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
        await self.api.disconnect()
