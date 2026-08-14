from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WattpilotEntity


SENSORS = [
    ("power", "Charging power", ("power", "power_total", "total_power"), UnitOfPower.WATT, SensorDeviceClass.POWER),
    ("energy", "Total energy", ("energy", "energy_total", "total_energy"), UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY),
    ("current", "Charging current", ("amp", "amps", "current"), UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
    ("voltage1", "Voltage L1", ("voltage1", "volt1"), UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
    ("voltage2", "Voltage L2", ("voltage2", "volt2"), UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
    ("voltage3", "Voltage L3", ("voltage3", "volt3"), UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
    ("current1", "Current L1", ("amps1", "amp1", "current1"), UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
    ("current2", "Current L2", ("amps2", "amp2", "current2"), UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
    ("current3", "Current L3", ("amps3", "amp3", "current3"), UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT),
    ("power1", "Power L1", ("power1",), UnitOfPower.WATT, SensorDeviceClass.POWER),
    ("power2", "Power L2", ("power2",), UnitOfPower.WATT, SensorDeviceClass.POWER),
    ("power3", "Power L3", ("power3",), UnitOfPower.WATT, SensorDeviceClass.POWER),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = entry.runtime_data
    async_add_entities(
        WattpilotValueSensor(coordinator, uid, name, aliases, unit, device_class)
        for uid, name, aliases, unit, device_class in SENSORS
    )


class WattpilotValueSensor(WattpilotEntity, SensorEntity):
    def __init__(self, coordinator, uid, name, aliases, unit, device_class):
        super().__init__(coordinator)
        self._attr_unique_id = f"wattpilot_{uid}"
        self._attr_name = name
        self._aliases = aliases
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING if uid == "energy" else SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = self.value(*self._aliases)
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
