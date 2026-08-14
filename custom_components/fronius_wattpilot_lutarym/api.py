from __future__ import annotations

from typing import Any

from wattpilot_api import Wattpilot


class WattpilotAPI:
    """Stable adapter around wattpilot-api.

    Keeping the third-party library behind this adapter makes it possible to
    update the Home Assistant integration without spreading library-specific
    assumptions throughout every entity platform.
    """

    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.client: Wattpilot | None = None

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
        finally:
            self.client = None

    @property
    def connected(self) -> bool:
        return self.client is not None

    @property
    def serial(self) -> str | None:
        return getattr(self.client, "serial", None) if self.client else None

    @property
    def firmware(self) -> str | None:
        return getattr(self.client, "firmware", None) if self.client else None

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
        if not self.client:
            return {}
        return dict(getattr(self.client, "all_properties", {}))

    def subscribe(self, callback) -> None:
        if self.client is None:
            raise RuntimeError("Wattpilot is not connected")
        self.client.on_property_change(callback)

    async def set_current(self, amperage: int) -> None:
        if not self.client:
            raise RuntimeError("Wattpilot is not connected")
        await self.client.set_power(amperage)

    async def set_mode(self, mode) -> None:
        if not self.client:
            raise RuntimeError("Wattpilot is not connected")
        await self.client.set_mode(mode)
