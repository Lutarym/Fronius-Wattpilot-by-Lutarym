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

_LOGGER = logging.getLogger(__name__)

# Abstand, in dem geprueft wird, ob die Verbindung noch steht
WATCHDOG_INTERVAL = timedelta(seconds=60)

# Wartezeit zwischen Wiederverbindungsversuchen, waechst bis zum Hoechstwert
RECONNECT_DELAY = 10
RECONNECT_DELAY_MAX = 300


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

    async def _async_update_data(self) -> dict[str, Any]:
        """Wird vom Ueberwachungszyklus aufgerufen."""
        if not self.api.connected:
            self.connected = False
            self._schedule_reconnect()
            return self.data or {}

        self.connected = True
        return self.api.properties()

    async def async_connect(self) -> None:
        """Baut die erste Verbindung auf."""
        try:
            await self.api.connect()
        except Exception as err:  # noqa: BLE001
            self.connected = False
            raise ConfigEntryNotReady(
                f"Verbindung zum Wattpilot nicht moeglich: {err}"
            ) from err

        self.connected = True
        self._reconnect_delay = RECONNECT_DELAY

        @callback
        def property_changed(name: str, value: Any) -> None:
            """Wird bei jeder Wertaenderung vom Geraet aufgerufen."""
            # Die Unter-Werte werden neu aufgeloest, damit zum Beispiel
            # eine Aenderung am Array nrg auch die Einzelwerte aktualisiert.
            self.async_set_updated_data(self.api.properties())

        self.api.subscribe(property_changed)
        self.async_set_updated_data(self.api.properties())

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

            @callback
            def property_changed(name: str, value: Any) -> None:
                self.async_set_updated_data(self.api.properties())

            self.api.subscribe(property_changed)
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
