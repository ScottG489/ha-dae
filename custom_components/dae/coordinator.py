"""Data update coordinator for the dae integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import DaeClient
from .const import LOGGER


class DaeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Data update coordinator for the dae integration."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, dae_client: DaeClient
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name="dae",
            update_interval=timedelta(seconds=60),
        )
        self.client = dae_client

    def _update(self) -> dict:
        """Fetch data for all meters."""
        return self.client.get_channel_meters()

    async def _async_update_data(self) -> str:
        """Send request to the executor."""
        return await self.hass.async_add_executor_job(self._update)

