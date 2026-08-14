from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WattpilotCoordinator


class WattpilotEntity(CoordinatorEntity[WattpilotCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: WattpilotCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.coordinator.api.serial or self.coordinator.api.host)
            },
            "name": self.coordinator.api.name,
            "manufacturer": "Fronius",
            "model": "Wattpilot",
            "sw_version": self.coordinator.api.firmware,
        }

    def value(self, *aliases):
        data = self.coordinator.data or {}
        for key in aliases:
            if key in data and data[key] is not None:
                return data[key]
        return None
