"""St-Patrick Residence Integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, Platform
from homeassistant.helpers.httpx_client import get_async_client

from .const import DOMAIN, LOGGER
from .coordinator import MenuUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


type MenuConfigEntry = ConfigEntry[MenuUpdateCoordinator]


PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up St-Patrick Platform."""
    coordinator = MenuUpdateCoordinator(
        hass,
        logger=LOGGER,
        client=get_async_client(hass),
        password=entry.data[CONF_PASSWORD],
    )
    entry.runtime_data = coordinator
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MenuConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MenuConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and not hass.config_entries.async_entries(DOMAIN):
        hass.data.pop(DOMAIN)
    return unload_ok
