"""Coordinator for all the sensors."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LiveTourApi, MenuData
from .const import DOMAIN

if TYPE_CHECKING:
    from logging import Logger

    from homeassistant.core import HomeAssistant
    from httpx import AsyncClient

    from . import MenuConfigEntry


class MenuUpdateCoordinator(DataUpdateCoordinator[MenuData]):
    """Class to manage fetch data from the API."""

    config_entry: MenuConfigEntry
    _api: LiveTourApi

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        client: AsyncClient,
        password: str,
    ) -> None:
        """Initialize coordinator."""
        self._api = LiveTourApi(client, password)
        super().__init__(hass, logger, name=DOMAIN, update_interval=timedelta(hours=1))

    async def _async_setup(self) -> None:
        """Set up API credentials."""
        await self._api.login()
        self.logger.debug("Successfully logged in to Live Tour API")

    async def _async_update_data(self) -> MenuData:
        """Fetch new data from API endpoint."""
        try:
            data = await self._api.get_menu_for_date(str(datetime.now().date()))
            self.logger.debug("Successfully fetched menu data: %s", data)
        except Exception as exception:
            raise UpdateFailed(exception) from exception
