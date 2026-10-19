# TEC Heat Pump (local Tuya)

A Home Assistant integration for heat pumps from TEC (The Energy Combination,
Oldenzaal, the Netherlands), talking to the unit directly over the
local Tuya protocol (via [tinytuya](https://github.com/jasonacox/tinytuya)). No cloud
polling: the unit pushes changes as they happen, and the integration keeps one
persistent connection open.

Tested on a **TEC RS07**. Other TEC models on the same Tuya module may work, but the
datapoints could differ.

> This is an unofficial, community project. It is not affiliated with, endorsed by or
> supported by The Energy Combination (TEC) or Tuya. Writing settings to your heat pump is at your own risk.

## Entities

**Controls**

| Entity | Type | Notes |
|---|---|---|
| Heating curve base temperature | number | ST02, 15–55 °C. The unit adds its own heating curve on top. |
| DHW setpoint | number | ST09, 30–60 °C |
| DHW | switch | Domestic hot water on/off |
| Power (manual mode) | switch | Only has effect when the unit is in manual control, not in thermostat mode |

**Sensors**

- Supply, return, outdoor and DHW tank temperature
- Room setpoint
- Compressor frequency
- Flow (m³/h)
- Heat output (kW), calculated from flow × (supply − return)
- Mode and fault code
- Pump, electric heater and gas boiler running state
- Diagnostic: discharge temperature, suction temperature, low-side pressure

Datapoints whose meaning isn't confirmed yet show up as raw `DP <n>` diagnostic entities.
They are disabled by default and read-only. See [datapoints.md](datapoints.md) for the
full datapoint reference.

Entities become unavailable when the unit hasn't sent anything for about 3 minutes.

## Installation

### HACS

1. In HACS, open the menu → **Custom repositories**.
2. Add `https://github.com/smitb/tec-heatpump` with type **Integration**.
3. Install **TEC Heat Pump (local Tuya)** and restart Home Assistant.

### Manual

Copy `custom_components/tec_heatpump` into your Home Assistant `config/custom_components/`
directory and restart Home Assistant.

## Configuration

Go to **Settings → Devices & services → Add integration → TEC Heat Pump (local Tuya)**
and enter:

- **IP address** of the heat pump's Wi-Fi module. Give it a fixed DHCP lease.
- **Tuya device ID** and **local key**
- **Protocol version**, usually `3.3`

The device ID and local key come from the Tuya cloud. The easiest way to get them is the
[tinytuya setup wizard](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys)
(`python -m tinytuya wizard`). The local key changes if you re-pair the unit in the
Smart Life / Tuya app.

The Tuya module accepts only a limited number of local connections. If setup fails with
"cannot connect", close other local clients (for example a tinytuya script or another
integration) and try again. The Smart Life app over the cloud doesn't interfere.

## License

[MIT](LICENSE)
