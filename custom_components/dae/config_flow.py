"""Config flow for dae integration."""
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from . import DaeClient
from .const import DOMAIN, LOGGER

CREDS_FORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the initial setup of a dae integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.api_key: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Prompt user for dae credentials."""
        return await self._show_creds_form()

    async def async_step_creds(self, user_input: dict[str, Any]) -> FlowResult:
        """Re-prompt for creds if invalid. Otherwise, create entry."""
        await self.async_set_unique_id(user_input[CONF_USERNAME])
        self._abort_if_unique_id_configured()

        dae_client = DaeClient(username=user_input[CONF_USERNAME], password=user_input[CONF_PASSWORD])
        login_response = await self.hass.async_add_executor_job(dae_client.login)
        if not login_response.result:
            return await self._show_error_creds_form()
        return self.async_create_entry(
            title="dae", data={"username": user_input[CONF_USERNAME], "password": user_input[CONF_PASSWORD]}
        )

    async def _show_creds_form(self) -> FlowResult:
        return self.async_show_form(
            step_id="creds", data_schema=CREDS_FORM_SCHEMA, last_step=True
        )

    async def _show_error_creds_form(self) -> FlowResult:
        LOGGER.error("Unauthorized")
        return self.async_show_form(
            step_id="creds",
            data_schema=CREDS_FORM_SCHEMA,
            errors={"base": "invalid_auth"},
            last_step=False,
        )
