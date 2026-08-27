"""Adapter um die Bibliothek wattpilot-api.

Die Bibliothek bleibt hinter diesem Adapter, damit die Integration
aktualisiert werden kann, ohne dass Annahmen ueber die Bibliothek in
jeder einzelnen Entitaets-Datei verstreut sind.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

from wattpilot_api import Wattpilot
from wattpilot_api.definition import get_all_properties, load_api_definition

_LOGGER = logging.getLogger(__name__)


def _plain(value: Any) -> Any:
    """Wandelt SimpleNamespace-Werte in einfache Python-Datentypen um."""
    if isinstance(value, SimpleNamespace):
        return {k: _plain(v) for k, v in value.__dict__.items()}
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


class WattpilotAPI:
    """Stabile Schnittstelle zum Wattpilot."""

    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.client: Wattpilot | None = None
        # Die API-Definition beschreibt auch die zusammengesetzten
        # Properties, zum Beispiel das Messwerte-Array nrg.
        self._api_def = load_api_definition(split_properties=True)

    async def connect(self) -> None:
        if self.client is not None:
            return

        self.client = Wattpilot(
            host=self.host,
            password=self.password,
            connect_timeout=20.0,
            init_timeout=30.0,
        )
        await self.client.connect()

    async def disconnect(self) -> None:
        if self.client is None:
            return
        try:
            await self.client.disconnect()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Fehler beim Trennen der Verbindung: %s", err)
        finally:
            self.client = None

    @property
    def connected(self) -> bool:
        return self.client is not None and self.client.connected

    @property
    def serial(self) -> str | None:
        return getattr(self.client, "serial", None) if self.client else None

    @property
    def firmware(self) -> str | None:
        return getattr(self.client, "firmware", None) if self.client else None

    @property
    def model(self) -> str | None:
        """Geraetemodell, zum Beispiel die Leistungsvariante."""
        if not self.client:
            return None
        variant = getattr(self.client, "variant", None)
        model = getattr(self.client, "model", None)
        if model and variant:
            return f"{model} {variant}"
        return model or variant

    @property
    def name(self) -> str:
        if not self.client:
            return "Fronius Wattpilot"
        return (
            getattr(self.client, "friendly_name", None)
            or getattr(self.client, "name", None)
            or "Fronius Wattpilot"
        )

    def properties(self) -> dict[str, Any]:
        """Alle Properties einschliesslich der zusammengesetzten Unter-Werte.

        Das Messwerte-Array nrg wird dabei in nrg_ul1, nrg_il1 und so
        weiter aufgeteilt, ebenso die Objekte wie sch_week oder awcp.
        """
        if not self.client:
            return {}
        raw = dict(getattr(self.client, "all_properties", {}))
        try:
            resolved = get_all_properties(self._api_def, raw)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Unter-Werte konnten nicht aufgeloest werden: %s", err)
            resolved = raw
        return {k: _plain(v) for k, v in resolved.items()}

    def subscribe(self, callback) -> None:
        if self.client is None:
            raise RuntimeError("Wattpilot ist nicht verbunden")
        self.client.on_property_change(callback)

    async def set_property(self, name: str, value: Any) -> None:
        """Setzt eine beliebige Property auf dem Geraet."""
        if not self.client:
            raise RuntimeError("Wattpilot ist nicht verbunden")
        await self.client.set_property(name, value)

    async def reboot(self) -> None:
        """Startet den Wattpilot neu."""
        await self.set_property("rst", True)
