from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import WattpilotEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = entry.runtime_data
    async_add_entities([
        WattpilotBinary(coordinator, "vehicle_connected", "Vehicle connected", ("car_connected", "carConnected"), BinarySensorDeviceClass.PLUG),
        WattpilotBinary(coordinator, "charging", "Charging", ("charging", "car_charging"), BinarySensorDeviceClass.BATTERY_CHARGING),
    ])


class WattpilotBinary(WattpilotEntity, BinarySensorEntity):
    def __init__(self, coordinator, uid, name, aliases, device_class):
        super().__init__(coordinator)
        self._attr_unique_id = f"wattpilot_{uid}"
        self._attr_name = name
        self._aliases = aliases
        self._attr_device_class = device_class

    @property
    def is_on(self):
        value = self.value(*self._aliases)
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)
