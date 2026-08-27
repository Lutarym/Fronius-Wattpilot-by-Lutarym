"""Adapter um die Bibliothek wattpilot-api.

Die Bibliothek bleibt hinter diesem Adapter, damit die Integration
aktualisiert werden kann, ohne dass Annahmen ueber die Bibliothek in
jeder einzelnen Entitaets-Datei verstreut sind.

Wichtig fuer Home Assistant: Die Bibliothek liest beim ersten Zugriff
eine YAML-Datei von der Festplatte. Das darf nicht im Event Loop
geschehen, weil es Home Assistant sonst kurzzeitig anhaelt. Alle solchen
Zugriffe laufen deshalb hier in einem Hintergrund-Thread und werden
danach im Speicher behalten.
"""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from typing import Any

from homeassistant.core import HomeAssistant
from wattpilot_api import Wattpilot
from wattpilot_api.definition import (
    ApiDefinition,
    get_all_properties,
    get_child_property_value,
    load_api_definition,
)

_LOGGER = logging.getLogger(__name__)

# Die API-Definition ist fuer alle Geraete gleich und wird daher nur
# einmal geladen und dann geteilt.
_definition_lock = asyncio.Lock()
_definition_split: ApiDefinition | None = None
_definition_flat: ApiDefinition | None = None


def _load_definitions() -> tuple[ApiDefinition, ApiDefinition]:
    """Laedt beide Fassungen der API-Definition. Laeuft im Hintergrund-Thread.

    Die aufgeteilte Fassung wird fuer die Unter-Werte gebraucht, zum
    Beispiel die Einzelwerte des Messwerte-Arrays. Die flache Fassung
    verwendet die Bibliothek selbst beim Schreiben von Werten.
    """
    return (
        load_api_definition(split_properties=True),
        load_api_definition(split_properties=False),
    )


async def async_prepare_definitions(hass: HomeAssistant) -> None:
    """Stellt sicher, dass die API-Definition geladen ist."""
    global _definition_split, _definition_flat  # noqa: PLW0603

    if _definition_split is not None and _definition_flat is not None:
        return

    async with _definition_lock:
        # Nach dem Warten erneut pruefen, ein anderer Vorgang war
        # moeglicherweise schneller.
        if _definition_split is not None and _definition_flat is not None:
            return
        _definition_split, _definition_flat = await hass.async_add_executor_job(
            _load_definitions
        )
        _LOGGER.debug("API-Definition geladen")


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

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        password: str,
    ) -> None:
        self.hass = hass
        self.host = host
        self.password = password
        self.client: Wattpilot | None = None

    @property
    def _api_def(self) -> ApiDefinition | None:
        return _definition_split

    def _create_client(self) -> Wattpilot:
        """Erzeugt den Client. Laeuft im Hintergrund-Thread."""
        client = Wattpilot(
            host=self.host,
            password=self.password,
            connect_timeout=20.0,
            init_timeout=30.0,
        )
        # Die Bibliothek wuerde die Definition sonst erst beim ersten
        # Schreibvorgang laden, und zwar im Event Loop. Deshalb wird ihr
        # Zwischenspeicher hier vorab gefuellt.
        if _definition_flat is not None:
            client._api_def_cache = _definition_flat  # noqa: SLF001
        return client

    async def connect(self) -> None:
        if self.client is not None:
            return

        await async_prepare_definitions(self.hass)
        self.client = await self.hass.async_add_executor_job(self._create_client)
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

    def raw_properties(self) -> dict[str, Any]:
        """Nur die Properties, die das Geraet selbst gemeldet hat.

        Ohne die zusammengesetzten Unter-Werte, die aus Eltern-Werten
        abgeleitet werden.
        """
        if not self.client:
            return {}
        return dict(getattr(self.client, "all_properties", {}))

    def available_keys(self) -> set[str]:
        """Alle Schluessel, die dieses Geraet tatsaechlich liefert.

        Ein Schluessel gilt als vorhanden, wenn das Geraet ihn gemeldet
        hat. Der Wert darf dabei leer sein, denn manche Properties sind
        im Ruhezustand bewusst leer, zum Beispiel die Transaktion, wenn
        gerade keine Karte aktiv ist.

        Bei zusammengesetzten Werten wie dem Messwerte-Array nrg muss
        zusaetzlich der abgeleitete Einzelwert vorhanden sein, denn nicht
        jedes Geraet fuellt das Array vollstaendig.
        """
        raw = self.raw_properties()
        if not raw:
            return set()

        verfuegbar = set(raw)
        api_def = self._api_def
        if api_def is None:
            return verfuegbar

        for child_key in api_def.split_properties:
            definition = api_def.properties.get(child_key, {})
            parent = definition.get("parentProperty")
            if not parent or parent not in raw:
                continue
            try:
                wert = get_child_property_value(api_def, raw, child_key)
            except Exception:  # noqa: BLE001
                continue
            if wert is not None:
                verfuegbar.add(child_key)

        return verfuegbar

    def properties(self) -> dict[str, Any]:
        """Alle Properties einschliesslich der zusammengesetzten Unter-Werte.

        Das Messwerte-Array nrg wird dabei in nrg_ul1, nrg_il1 und so
        weiter aufgeteilt, ebenso die Objekte wie sch_week oder awcp.
        """
        raw = self.raw_properties()
        if not raw:
            return {}

        api_def = self._api_def
        if api_def is None:
            return {k: _plain(v) for k, v in raw.items()}

        try:
            resolved = get_all_properties(api_def, raw)
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
