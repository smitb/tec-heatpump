from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TecConfigEntry
from .const import DP_FLOW, DP_RETURN, DP_SUPPLY, DPS, WATER_KW_PER_M3H_K, TecDp
from .coordinator import TecCoordinator
from .entity import TecEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: TecConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        TecSensor(coordinator, d) for d in DPS if d.platform == "sensor"
    ]
    entities.append(TecHeatOutputSensor(coordinator))
    async_add_entities(entities)


class TecSensor(TecEntity, SensorEntity):
    def __init__(self, coordinator, desc) -> None:
        super().__init__(coordinator, desc)
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_state_class = desc.state_class
        if desc.scale != 1:
            # One decimal per factor of ten in the scale (0.1 m³/h, 0.1 °C, ...).
            self._attr_suggested_display_precision = len(str(int(desc.scale))) - 1

    @property
    def native_value(self):
        return self.scaled


def heat_output_kw(dps: dict) -> float | None:
    """Thermal output from flow (0.1 m³/h) and supply/return (0.1 °C)."""
    try:
        flow = dps[DP_FLOW] / 10
        delta_t = (dps[DP_SUPPLY] - dps[DP_RETURN]) / 10
    except (KeyError, TypeError):
        return None
    # Negative during defrost (heat is taken from the water); report that as 0.
    return round(max(flow * delta_t * WATER_KW_PER_M3H_K, 0), 2)


class TecHeatOutputSensor(TecEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: TecCoordinator) -> None:
        super().__init__(coordinator, TecDp(dp=DP_FLOW, key="heat_output", platform="sensor"))

    @property
    def native_value(self) -> float | None:
        return heat_output_kw(self.coordinator.data or {})
