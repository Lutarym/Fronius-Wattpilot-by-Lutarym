"""Gemeinsame Basisklasse aller Wattpilot-Entitaeten."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WattpilotDescription
from .coordinator import WattpilotCoordinator

CATEGORY_MAP = {
    "config": EntityCategory.CONFIG,
    "diagnostic": EntityCategory.DIAGNOSTIC,
}


def geraetekennung(coordinator: WattpilotCoordinator) -> str:
    """Die dauerhafte Kennung dieses Wattpilot.

    Sie geht in die eindeutige Kennung jeder Entitaet und in die
    Geraetekennung ein und darf sich deshalb nie aendern.

    Zuerst wird die Seriennummer des Geraets genommen. Meldet der
    Wattpilot sie gerade nicht, wird auf die beim Einrichten
    gespeicherte Kennung zurueckgegriffen und erst danach auf die
    Kennung des Konfigurationseintrags. Ohne diesen Rueckfall wuerde
    ein einziger Start ohne Seriennummer saemtliche Entitaeten und das
    Geraet selbst ein zweites Mal anlegen.
    """
    return (
        coordinator.api.serial
        or coordinator.entry.unique_id
        or coordinator.entry.entry_id
    )


class WattpilotEntity(CoordinatorEntity[WattpilotCoordinator]):
    """Basis fuer jede Entitaet, die einer Property entspricht."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WattpilotCoordinator,
        description: WattpilotDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description_data = description

        self._attr_unique_id = f"{geraetekennung(coordinator)}_{description.key}"
        # Der Anzeigename kommt aus den Sprachdateien unter translations/
        self._attr_translation_key = description.translation_key
        self._attr_entity_registry_enabled_default = description.enabled

        # Vermerken, dass diese Entitaet angelegt wurde. Damit weiss die
        # Integration hinterher, welche Eintraege im Register noch von
        # frueheren Fassungen stammen und aufgeraeumt werden koennen.
        coordinator.angelegte_kennungen.add(self._attr_unique_id)

        if description.category:
            self._attr_entity_category = CATEGORY_MAP.get(description.category)

        # Einmal berechnen statt bei jedem Zugriff. Home Assistant fragt
        # device_info haeufig ab, und die Angaben aendern sich innerhalb
        # einer Sitzung nicht.
        api = coordinator.api
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, geraetekennung(coordinator))},
            name=api.name,
            manufacturer="Fronius",
            model=api.model or "Wattpilot",
            sw_version=api.firmware,
            serial_number=api.serial,
            configuration_url=f"http://{api.host}",
        )

    @property
    def available(self) -> bool:
        """Die Entitaet ist nur bei stehender Verbindung verfuegbar."""
        return self.coordinator.connected and super().available

    @property
    def raw_value(self) -> Any:
        """Der unveraenderte Wert der Property."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description_data.key)

    async def async_write_value(self, value: Any) -> None:
        """Schreibt einen neuen Wert auf das Geraet."""
        await self.coordinator.async_set_property(
            self.entity_description_data.key, value
        )
