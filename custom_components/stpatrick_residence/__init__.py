"""St-Patrick Residence Integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_PASSWORD,
    Platform,
)
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONFIG_VERSION, DOMAIN
from .coordinator import MenuUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant


type MenuConfigEntry = ConfigEntry[MenuUpdateCoordinator]


PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up St-Patrick Platform."""
    menu_coordinator = MenuUpdateCoordinator(
        hass,
        entry.data[CONF_PASSWORD],
    )

    startup_task = hass.async_create_task(mug_coordinator.async_config_entry_first_refresh())

    entry.runtime_data = menu_coordinator
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MenuConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
