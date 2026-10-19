from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TecConfigEntry
from .const import DPS
from .entity import TecEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: TecConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        TecBinarySensor(entry.runtime_data, d) for d in DPS if d.platform == "binary_sensor"
    )


class TecBinarySensor(TecEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        return None if self.raw is None else bool(self.raw)
