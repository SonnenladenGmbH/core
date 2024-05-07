"""Test the APsystems Local API config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.components.apsystems_local.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form_cannot_connect_and_recover(
    hass: HomeAssistant, mock_setup_entry
) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.apsystems_local.config_flow.APsystemsEZ1M",
        return_value=AsyncMock(),
    ) as mock_api:
        mock_api.side_effect = TimeoutError
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_IP_ADDRESS: "127.0.0.2",
                CONF_NAME: "Solar",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "connection_refused"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.
    with patch(
        "homeassistant.components.apsystems_local.config_flow.APsystemsEZ1M",
        return_value=AsyncMock(),
    ) as mock_api:
        mock_api.return_value.get_device_info = AsyncMock(True)
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "127.0.0.1",
                CONF_NAME: "Solar",
            },
        )
        # AiohttpClientMockResponse does not have .ok
        # So, I check if it's coming that far and fail if that's not the case
        assert result2.get("type") == FlowResultType.CREATE_ENTRY
        assert result2["data"].get(CONF_IP_ADDRESS) == "127.0.0.1"
        assert result2["data"].get(CONF_NAME) == "Solar"


async def test_form_cannot_connect(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.apsystems_local.config_flow.APsystemsEZ1M",
        return_value=AsyncMock(),
    ) as mock_api:
        mock_api.side_effect = TimeoutError
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_IP_ADDRESS: "127.0.0.2",
                CONF_NAME: "Solar",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "connection_refused"}


async def test_form_create_success(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test we handle creatinw with success."""
    with patch(
        "homeassistant.components.apsystems_local.config_flow.APsystemsEZ1M",
        return_value=AsyncMock(),
    ) as mock_api:
        mock_api.return_value.get_device_info = AsyncMock(True)
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={
                CONF_IP_ADDRESS: "127.0.0.1",
                CONF_NAME: "Solar",
            },
        )
        # AiohttpClientMockResponse does not have .ok
        # So, I check if it's coming that far and fail if that's not the case
        assert result.get("type") == FlowResultType.CREATE_ENTRY
        assert result["data"].get(CONF_IP_ADDRESS) == "127.0.0.1"
        assert result["data"].get(CONF_NAME) == "Solar"
