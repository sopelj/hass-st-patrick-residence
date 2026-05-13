"""Test Sensor entities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from .conftest import setup_platform

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from custom_components.stpatrick_residence.api import LiveTourApi


async def test_setup_sensors(
    hass: HomeAssistant,
    mock_api: LiveTourApi,
) -> None:
    """Initialize and test sensors."""
    assert len(hass.states.async_all()) == 0

    mock_api.get_menu_for_date = AsyncMock(return_value=[])

    await setup_platform(hass, mock_api, AsyncMock())
    await hass.async_block_till_done()
    assert len(hass.states.async_all()) == 5
