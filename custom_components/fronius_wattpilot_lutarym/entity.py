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

        serial = coordinator.api.serial or coordinator.entry.entry_id
        self._attr_unique_id = f"{serial}_{description.key}"
        # Der Anzeigename kommt aus den Sprachdateien unter translations/
        self._attr_translation_key = description.translation_key
        self._attr_entity_registry_enabled_default = description.enabled

        if description.category:
            self._attr_entity_category = CATEGORY_MAP.get(description.category)

    @property
    def device_info(self) -> DeviceInfo:
        api = self.coordinator.api
        serial = api.serial or self.coordinator.entry.entry_id
        return DeviceInfo(
            identifiers={(DOMAIN, serial)},
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
