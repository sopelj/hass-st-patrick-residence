"""Coordinator for all the sensors."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import LiveTourApi, MenuData
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)


class MenuUpdateCoordinator(DataUpdateCoordinator[MenuData]):
    """Class to manage fetch data from the API."""

    _api: LiveTourApi

    def __init__(
        self,
        hass: HomeAssistant,
        password: str,
    ) -> None:
        """Initialize coordinator."""
        self._api = LiveTourApi(get_async_client(hass), password)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=60))

    async def _async_setup(self) -> None:
        """Set up API credentials."""
        await self._api.login()

    async def _async_update_data(self) -> list[MenuData]:
        """Fetch new data from API endpoint."""
        data = await self._api.get_menu_for_date(str(datetime.now().date()))
        self.async_update_listeners()
        return data
