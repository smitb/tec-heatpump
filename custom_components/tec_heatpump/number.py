from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TecConfigEntry
from .const import DPS
from .entity import TecEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: TecConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(TecNumber(entry.runtime_data, d) for d in DPS if d.platform == "number")


class TecNumber(TecEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, desc) -> None:
        super().__init__(coordinator, desc)
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_native_min_value = desc.min_value
        self._attr_native_max_value = desc.max_value
        self._attr_native_step = desc.step

    @property
    def native_value(self) -> float | None:
        return self.scaled

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_dp(self.desc.dp, round(value * self.desc.scale))
