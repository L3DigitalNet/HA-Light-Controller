# Entity Device Class Reference

## Sensor Device Classes

| Device Class | Unit Examples | Use Case |
|---|---|---|
| `APPARENT_POWER` | VA | Apparent power |
| `AQI` | — | Air Quality Index |
| `ATMOSPHERIC_PRESSURE` | hPa, mbar | Barometric pressure |
| `BATTERY` | % | Battery charge level |
| `CO` | ppm | Carbon monoxide concentration |
| `CO2` | ppm | Carbon dioxide concentration |
| `CURRENT` | A, mA | Electrical current |
| `DATA_RATE` | bit/s, kbit/s, Mbit/s | Network throughput |
| `DATA_SIZE` | bit, kB, MB, GB, TB | Storage or transfer size |
| `DATE` | — | Date only (no time) |
| `DISTANCE` | km, m, cm, mm, mi, ft | Distance measurement |
| `DURATION` | d, h, min, s, ms | Time duration |
| `ENERGY` | Wh, kWh, MWh, GJ | Energy consumption |
| `ENERGY_STORAGE` | Wh, kWh, MWh | Stored energy |
| `ENUM` | — | Fixed set of string values |
| `FREQUENCY` | Hz, kHz, MHz, GHz | Signal frequency |
| `GAS` | m³, ft³, CCF | Gas volume |
| `HUMIDITY` | % | Relative humidity |
| `ILLUMINANCE` | lx | Light level |
| `IRRADIANCE` | W/m², BTU/(h⋅ft²) | Solar irradiance |
| `MOISTURE` | % | Soil or material moisture |
| `MONETARY` | — | Currency value |
| `NITROGEN_DIOXIDE` | µg/m³ | NO2 concentration |
| `NITROGEN_MONOXIDE` | µg/m³ | NO concentration |
| `OZONE` | µg/m³ | O3 concentration |
| `PH` | — | Acidity/alkalinity |
| `PM1` | µg/m³ | Particulate matter ≤1µm |
| `PM10` | µg/m³ | Particulate matter ≤10µm |
| `PM25` | µg/m³ | Particulate matter ≤2.5µm |
| `POWER` | W, kW, MW | Electrical power |
| `POWER_FACTOR` | %, None | Power factor |
| `PRECIPITATION` | cm, in, mm | Rainfall amount |
| `PRECIPITATION_INTENSITY` | in/d, in/h, mm/d, mm/h | Rainfall rate |
| `PRESSURE` | Pa, kPa, hPa, bar, psi, mmHg | Pressure |
| `REACTIVE_POWER` | var | Reactive power |
| `SIGNAL_STRENGTH` | dB, dBm | Wireless signal |
| `SOUND_PRESSURE` | dB, dBA | Sound level |
| `SPEED` | ft/s, km/h, m/s, mph, kn | Velocity |
| `SULPHUR_DIOXIDE` | µg/m³ | SO2 concentration |
| `TEMPERATURE` | °C, °F, K | Temperature |
| `TIMESTAMP` | — | ISO 8601 datetime |
| `VOLATILE_ORGANIC_COMPOUNDS` | µg/m³ | VOC concentration |
| `VOLTAGE` | V, mV, µV | Electrical voltage |
| `VOLUME` | L, mL, gal, fl. oz., m³, ft³, CCF | Volume |
| `VOLUME_FLOW_RATE` | m³/h, ft³/min, L/min, gal/min | Flow rate |
| `VOLUME_STORAGE` | L, mL, gal, fl. oz., m³, ft³, CCF | Stored volume |
| `WATER` | L, gal, m³, ft³, CCF | Water consumption |
| `WEIGHT` | kg, g, mg, µg, oz, lb, st | Mass |
| `WIND_SPEED` | ft/s, km/h, kn, m/s, mph | Wind velocity |

## State Classes

| State Class | When to Use |
|---|---|
| `MEASUREMENT` | Instantaneous reading (temperature, humidity, power) |
| `TOTAL` | Running total that can reset (gas meter after utility reset) |
| `TOTAL_INCREASING` | Running total that only goes up (energy meter, rain gauge) |

State class determines how Home Assistant calculates long-term statistics. Always set it for numeric sensors.

## Binary Sensor Device Classes

| Device Class | On Meaning | Off Meaning |
|---|---|---|
| `BATTERY` | Low | Normal |
| `BATTERY_CHARGING` | Charging | Not charging |
| `CO` | CO detected | Clear |
| `COLD` | Cold | Normal |
| `CONNECTIVITY` | Connected | Disconnected |
| `DOOR` | Open | Closed |
| `GARAGE_DOOR` | Open | Closed |
| `GAS` | Gas detected | Clear |
| `HEAT` | Hot | Normal |
| `LIGHT` | Light detected | No light |
| `LOCK` | Unlocked | Locked |
| `MOISTURE` | Wet | Dry |
| `MOTION` | Motion detected | Clear |
| `MOVING` | Moving | Not moving |
| `OCCUPANCY` | Occupied | Clear |
| `OPENING` | Open | Closed |
| `PLUG` | Plugged in | Unplugged |
| `POWER` | Power detected | No power |
| `PRESENCE` | Present | Away |
| `PROBLEM` | Problem | OK |
| `RUNNING` | Running | Not running |
| `SAFETY` | Unsafe | Safe |
| `SMOKE` | Smoke detected | Clear |
| `SOUND` | Sound detected | Clear |
| `TAMPER` | Tampering | Clear |
| `UPDATE` | Update available | Up-to-date |
| `VIBRATION` | Vibration | Clear |
| `WINDOW` | Open | Closed |

## Cover Device Classes

`AWNING`, `BLIND`, `CURTAIN`, `DAMPER`, `DOOR`, `GARAGE`, `GATE`, `SHADE`, `SHUTTER`, `WINDOW`

## Switch Device Classes

`OUTLET`, `SWITCH`

## Button Device Classes

`IDENTIFY`, `RESTART`, `UPDATE`
