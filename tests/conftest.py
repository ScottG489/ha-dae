"""Configure tests for the DAE integration."""
import json
from collections.abc import Awaitable, Callable

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.dae.client import LoginResponse


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


ComponentSetup = Callable[[], Awaitable[None]]

CONF_USER_ID = "user_id"
CONF_USER_EMAIL = "user_email"
CONF_BOARD_IDS = "board_ids"


def mock_fixture(path):
    """Mock response from DAE client."""
    return json.loads(load_fixture(path))


@pytest.fixture(name="mock_login_response")
def mock_login_response() -> Callable:
    """Fixture for a successful login."""
    def func(self) -> None:
        return LoginResponse.from_response(mock_fixture("login.json"))

    return func

@pytest.fixture(name="mock_login_response_fail")
def mock_login_response_fail() -> Callable:
    """Fixture for a login failure."""
    def func(self) -> None:
        return LoginResponse.from_response(mock_fixture("failed_request.json"))

    return func
