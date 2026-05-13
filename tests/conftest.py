"""Configure pytest."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import CONF_PASSWORD
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (  # type: ignore[import-untyped]
    MockConfigEntry,
)

from custom_components.stpatrick_residence.api import LiveTourApi
from custom_components.stpatrick_residence.const import DOMAIN
from custom_components.stpatrick_residence.coordinator import MenuUpdateCoordinator

if TYPE_CHECKING:
    from logging import Logger

    from homeassistant.core import HomeAssistant
    from httpx import AsyncClient


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def _auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""


@pytest.fixture
def mock_api() -> LiveTourApi:
    """Create a mocked Delire API instance."""
    mock_client = AsyncMock()
    api = LiveTourApi(mock_client, "fakepassword")
    api.login = AsyncMock()
    return api


async def setup_platform(
    hass: HomeAssistant,
    api: LiveTourApi,
    mock_client: AsyncMock | None = None,
    config_entry: MockConfigEntry | None = None,
) -> MockConfigEntry:
    """Load the integration with the provided gym(s)."""
    if config_entry is None:
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_PASSWORD: "fakepassword"},
        )

    await async_setup_component(hass, DOMAIN, {})
    config_entry.add_to_hass(hass)

    def get_coordinator(hass: HomeAssistant, logger: Logger, client: AsyncClient, password: str) -> MenuUpdateCoordinator:
        coordinator = MenuUpdateCoordinator(hass, Mock(), mock_client, password)
        coordinator._api = api
        return coordinator

    with (
        patch("custom_components.stpatrick_residence.get_async_client", lambda x: mock_client),
        patch("custom_components.stpatrick_residence.MenuUpdateCoordinator", get_coordinator),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    return config_entry
