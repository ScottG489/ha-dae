"""Test the DAE config flow."""
from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.dae.client import LoginResponse
from custom_components.dae.const import DOMAIN

USERNAME = "a_username"
PASSWORD = "abc123"

USER_INPUT_CREDS = {"username": USERNAME, "password": PASSWORD}


async def test_flow_user(hass: HomeAssistant, mock_login_response: LoginResponse) -> None:
    """Test full user setup flow."""
    init_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
            "custom_components.dae.config_flow.DaeClient.login",
            new=mock_login_response,
    ):
        creds_result = await hass.config_entries.flow.async_configure(
            init_result["flow_id"], user_input=USER_INPUT_CREDS
        )

    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "creds"
    assert init_result["last_step"] is True

    assert creds_result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert creds_result["data"] == {
        "username": USERNAME,
        "password": PASSWORD
    }
    assert creds_result["result"].unique_id == USERNAME
    assert creds_result["result"].title == USERNAME


async def test_flow_user_already_configured(hass: HomeAssistant, mock_login_response: LoginResponse) -> None:
    """Test full user setup flow."""
    init_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
            "custom_components.dae.config_flow.DaeClient.login",
            new=mock_login_response,
    ):
        await hass.config_entries.flow.async_configure(
            init_result["flow_id"], user_input=USER_INPUT_CREDS
        )

    init_result2 = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
            "custom_components.dae.config_flow.DaeClient.login",
            new=mock_login_response,
    ):
        creds_result = await hass.config_entries.flow.async_configure(
            init_result2["flow_id"], user_input=USER_INPUT_CREDS
        )

    assert creds_result["type"] == FlowResultType.ABORT
    assert creds_result["reason"] == "already_configured"

async def test_flow_user_fail(hass: HomeAssistant, mock_login_response_fail: LoginResponse) -> None:
    """Test user setup flow failure."""
    init_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
            "custom_components.dae.config_flow.DaeClient.login",
            new=mock_login_response_fail,
    ):
        creds_result = await hass.config_entries.flow.async_configure(
            init_result["flow_id"], user_input=USER_INPUT_CREDS
        )

    assert init_result["type"] == FlowResultType.FORM
    assert init_result["step_id"] == "creds"
    assert init_result["last_step"] is True

    assert creds_result["type"] == FlowResultType.FORM
    assert creds_result["step_id"] == "creds"
    assert creds_result["last_step"] is True
    assert creds_result["errors"] == {"base": 'invalid_auth'}
