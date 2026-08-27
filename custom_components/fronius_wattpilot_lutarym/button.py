"""Schaltflaechen fuer Geraetebefehle."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PROP_REBOOT, WattpilotDescription
from .entity import WattpilotEntity

REBOOT_DESCRIPTION = WattpilotDescription(
    key=PROP_REBOOT,
    translation_key="reboot",
    enabled=False,
    category="config",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([WattpilotRebootButton(coordinator, REBOOT_DESCRIPTION)])


class WattpilotRebootButton(WattpilotEntity, ButtonEntity):
    """Startet den Wattpilot neu."""

    _attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        await self.coordinator.api.reboot()
