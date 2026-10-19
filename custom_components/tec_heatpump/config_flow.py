"""Config flow for the TEC heat pump."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DEFAULT_PROTOCOL_VERSION,
    DOMAIN,
)
from .coordinator import create_device

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Required(CONF_LOCAL_KEY): str,
        vol.Required(CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION): vol.In(
            ["3.1", "3.3", "3.4", "3.5"]
        ),
    }
)


def _probe(data: dict[str, Any]) -> dict:
    device = create_device(
        data[CONF_HOST], data[CONF_DEVICE_ID], data[CONF_LOCAL_KEY], data[CONF_PROTOCOL_VERSION]
    )
    try:
        return device.status()
    finally:
        device.close()


class TecConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            try:
                result = await self.hass.async_add_executor_job(_probe, user_input)
            except Exception:  # noqa: BLE001
                result = None
            if not result or "dps" not in result:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="TEC heat pump", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(SCHEMA, user_input or {}),
            errors=errors,
        )
