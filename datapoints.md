## Available Data Points

### Writable (remote control)

| DP | Parameter | Description |
|----|-----------|-------------|
| 1 | `switch` | Heat pump on / off |
| 8 | `instant_heating` | DHW (domestic hot water) on / off |
| 4 | `temp_set` | Heating circuit setpoint ST02 (Â°C Ã— 10) |
| 101 | `dhw_temp_set` | DHW setpoint ST09 (Â°C Ã— 10) |
| 102 | `room_temp_set` | Room temperature setpoint ST19 (Â°C Ã— 10) |
| 106 | `heat_comp` | **Heating curve compensation factor ST06** |
| 5 | `work_mode` | Operating mode (smart / eco) |
| 103 | `min_outlet_prot` | Low outlet water protection threshold AR01 |

### Read-only sensors

| DP | Parameter | Description |
|----|-----------|-------------|
| 25 | `temp_effluent` | Outlet water temperature â€” supply (Â°C) |
| 22 | `temp_bottom` | Inlet water temperature â€” return (Â°C) |
| 26 | `temp_around` | Ambient outdoor temperature (Â°C) |
| 21 | `temp_top` | DHW tank temperature (Â°C) |
| 24 | `temp_venting` | Discharge gas temperature (Â°C) |
| 16 | `temp_current` | Suction gas temperature (Â°C) |
| 23 | `temp_coiler` | Low-side refrigerant pressure / LPS (bar) |
| 20 | `compressor_strength` | Compressor frequency (Hz) |
| 104 | `room_temp` | Room temperature from sensor (Â°C) |
| 15 | `unit_state` | Operating state: heating / cooling / DHW / defrost / standby |
| 32 | `ele_heating_state` | Electric / auxiliary heater active |
| 108 | `fault_code` | Active fault code (`NONE` = no fault) |
| 109 | `room_temp_2` | Zone 2 room temperature (Â°C) |
| 105 | `heat_mode_state` | Heating circuit mode string |
| 110 | `dhw_mode_state` | DHW mode string |

> **Note:** DP 106 (ST06 heating curve compensation) was confirmed writable by observing
> live changes made via Smart Life while monitoring the local protocol. The full list was
> validated against a running TEC RS07 heat pump.

## Observed on the local protocol (2026-10-14, tinytuya 3.3, unit heating)

`status()`, `detect_available_dps()` and an explicit DP query for 2–7/103/106/110–113 return only these DPs.
**DP 5, 103, 106 and 110 are not reported locally.** Raw values are shown; ÷10 where marked.

| DP | Raw | Interpretation | Status |
|----|-----|----------------|--------|
| 1 | `false` | on/off in manual-control mode (writable); ignored in thermostat mode, hence `false` while running | ok |
| 4 | 235 | 23.5 °C heating setpoint | ok |
| 8 | `false` | DHW on/off | ok |
| 15 | 0 | int state (defrost app expects `4` = defrost?) | unclear |
| 16 | 117 | 11.7 °C suction | ok |
| 20 | 30 | compressor Hz | ok |
| 21 | 0 | DHW tank temp (no tank sensor?) | ok |
| 22 | 285 | 28.5 °C inlet / return | ok |
| 23 | 87 | 8.7 bar LPS | ok |
| 24 | 461 | 46.1 °C discharge | ok |
| 25 | 305 | 30.5 °C outlet / supply | ok |
| 26 | 127 | 12.7 °C ambient | ok |
| 27 | `false` | compressor state? (false while 30 Hz) | unclear |
| 28 | `true` | 4-way valve | unclear |
| 30 | `true` | pump | ok |
| 32 | `false` | electric heater | ok |
| 34 | 200 | 20.0 °C room setpoint | likely |
| 39 | 0 | unknown | unknown |
| 101 | 500 | 50.0 °C DHW setpoint | ok |
| 102 | 130 | 13.0 — cooling setpoint (script) vs room setpoint (cloud doc) | unclear |
| 104 | 190 | 19.0 — HPS bar (script) vs room temp °C (cloud doc) | unclear |
| 105 | `"heating"` | mode string | ok |
| 107 | 8 | flow, 0.1 m³/h (COP check vs outdoor kWh meter ≈ 4.0) | ok |
| 108 | `"NONE"` | fault code | ok |
| 109 | `false` | boolean → gas boiler, not zone-2 temp | ok |

The device pushes partial updates unprompted every few seconds (e.g. `{"26": 130}`), so local push works.
