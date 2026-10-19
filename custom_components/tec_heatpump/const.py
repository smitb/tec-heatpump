"""Constants and the DP table for the TEC heat pump.

The DP table is based on what the unit actually reports on the local protocol
(see datapoints.md, "Observed on the local protocol"). DPs whose
meaning is not yet confirmed are exposed as raw diagnostic entities, disabled by
default, and are never writable.
"""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "tec_heatpump"

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"
DEFAULT_PROTOCOL_VERSION = "3.3"

# Water: 4.186 kJ/(kg·K) × 1000 kg/m³ / 3600 s/h → kW per (m³/h · K).
WATER_KW_PER_M3H_K = 1.163

DP_FLOW = "107"
DP_SUPPLY = "25"
DP_RETURN = "22"

# Ask the device for a full status this often (it also pushes changes on its own).
STATUS_INTERVAL = 60
# Mark entities unavailable when nothing has been received for this long.
STALE_AFTER = 180


@dataclass(frozen=True, kw_only=True)
class TecDp:
    """One Tuya datapoint and how it maps to Home Assistant."""

    dp: str
    key: str
    platform: str  # sensor | binary_sensor | switch | number
    scale: float = 1  # raw value / scale = HA value
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None
    diagnostic: bool = False
    enabled_default: bool = True
    icon: str | None = None


DPS: tuple[TecDp, ...] = (
    # --- Controls ---------------------------------------------------------
    # ST02: base temperature of the heating curve (the unit adds its own curve on top).
    TecDp(dp="4", key="heating_base_setpoint", platform="number", scale=10,
          unit="°C", device_class="temperature",
          min_value=15, max_value=55, step=0.5, icon="mdi:chart-bell-curve-cumulative"),
    # ST09: DHW setpoint.
    TecDp(dp="101", key="dhw_setpoint", platform="number", scale=10,
          unit="°C", device_class="temperature",
          min_value=30, max_value=60, step=1, icon="mdi:water-boiler"),
    TecDp(dp="8", key="dhw", platform="switch", icon="mdi:water-boiler"),
    # On/off when the unit is set to manual control; has no effect in thermostat mode.
    TecDp(dp="1", key="power", platform="switch", icon="mdi:power"),
    # --- Temperatures -----------------------------------------------------
    TecDp(dp="25", key="outlet_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement"),
    TecDp(dp="22", key="inlet_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement"),
    TecDp(dp="26", key="ambient_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement"),
    TecDp(dp="21", key="dhw_tank_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement"),
    TecDp(dp="24", key="discharge_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement", diagnostic=True),
    TecDp(dp="16", key="suction_temp", platform="sensor", scale=10, unit="°C",
          device_class="temperature", state_class="measurement", diagnostic=True),
    TecDp(dp="34", key="room_setpoint", platform="sensor", scale=10, unit="°C",
          device_class="temperature"),
    # --- Operation --------------------------------------------------------
    TecDp(dp="20", key="compressor_freq", platform="sensor", unit="Hz",
          device_class="frequency", state_class="measurement"),
    TecDp(dp="23", key="low_pressure", platform="sensor", scale=10, unit="bar",
          device_class="pressure", state_class="measurement", diagnostic=True),
    # 0.1 m³/h; checked against the outdoor-unit kWh meter (gives COP ~4, L/min gives 2.4).
    TecDp(dp="107", key="flow", platform="sensor", scale=10, unit="m³/h",
          device_class="volume_flow_rate", state_class="measurement"),
    TecDp(dp="105", key="mode", platform="sensor", icon="mdi:heat-pump"),
    TecDp(dp="108", key="fault", platform="sensor", icon="mdi:alert-circle"),
    TecDp(dp="30", key="pump", platform="binary_sensor", device_class="running"),
    TecDp(dp="32", key="electric_heater", platform="binary_sensor", device_class="running"),
    TecDp(dp="109", key="gas_boiler", platform="binary_sensor", device_class="running"),
    # --- Not yet confirmed: raw, read-only, disabled by default -----------
    TecDp(dp="15", key="dp_15", platform="sensor", diagnostic=True, enabled_default=False),
    TecDp(dp="27", key="dp_27", platform="binary_sensor", diagnostic=True, enabled_default=False),
    TecDp(dp="28", key="dp_28", platform="binary_sensor", diagnostic=True, enabled_default=False),
    TecDp(dp="39", key="dp_39", platform="sensor", diagnostic=True, enabled_default=False),
    TecDp(dp="102", key="dp_102", platform="sensor", scale=10, diagnostic=True,
          enabled_default=False),
    TecDp(dp="104", key="dp_104", platform="sensor", scale=10, diagnostic=True,
          enabled_default=False),
)

KNOWN_DPS = {d.dp for d in DPS}
