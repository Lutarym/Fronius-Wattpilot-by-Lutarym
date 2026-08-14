from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import WattpilotAPI

_LOGGER = logging.getLogger(__name__)


class WattpilotCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Own the persistent Wattpilot WebSocket connection."""

    def __init__(self, hass: HomeAssistant, api: WattpilotAPI) -> None:
        self.api = api
        self.connected = False
        self.last_update = None
        super().__init__(
            hass,
            _LOGGER,
            name="Fronius Wattpilot by Lutarym",
            update_interval=None,
        )

    async def async_connect(self) -> None:
        try:
            await self.api.connect()
            self.connected = True
            self.last_update = self.hass.loop.time()

            @callback
            def property_changed(name: str, value: Any) -> None:
                if self.data is None:
                    self.data = {}
                self.data[name] = value
                self.last_update = self.hass.loop.time()
                self.async_set_updated_data(dict(self.data))

            self.api.subscribe(property_changed)
            self.async_set_updated_data(self.api.properties())

        except Exception as err:
            self.connected = False
            raise ConfigEntryNotReady(
                f"Unable to connect to Wattpilot: {err}"
            ) from err

    async def async_reconnect(self) -> None:
        self.connected = False
        await self.api.disconnect()
        await asyncio.sleep(1)
        await self.async_connect()

    async def async_shutdown(self) -> None:
        self.connected = False
        await self.api.disconnect()
