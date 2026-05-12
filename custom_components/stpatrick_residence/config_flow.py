"""Add Config Flow for St-Patrick Residence."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD

from .const import DOMAIN, CONFIG_VERSION

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for St-Patrick Residence component."""

    VERSION = CONFIG_VERSION

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """First step for users."""
        errors: dict[str, str] = {}
        if user_input:
            return self.async_create_entry(title="St-Patrick Residence", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PASSWORD): str,
            },
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
