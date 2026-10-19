from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TecConfigEntry
from .const import DPS
from .entity import TecEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: TecConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(TecSwitch(entry.runtime_data, d) for d in DPS if d.platform == "switch")


class TecSwitch(TecEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        return None if self.raw is None else bool(self.raw)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self.desc.dp, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self.desc.dp, False)
