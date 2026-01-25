<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand-images/dark_logo.png">
  <source media="(prefers-color-scheme: light)" srcset="brand-images/logo.png">
  <img alt="HA Light Controller" src="brand-images/logo.png" width="200">
</picture>

# HA Light Controller

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/L3DigitalNet/HA-Light-Controller.svg)](https://github.com/L3DigitalNet/HA-Light-Controller/releases)
[![License](https://img.shields.io/github/license/L3DigitalNet/HA-Light-Controller.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/L3DigitalNet/HA-Light-Controller.svg)](https://github.com/L3DigitalNet/HA-Light-Controller/issues)

HA Light Controller adds state verification and automatic retries to light commands. When you call `light.turn_on`, Home Assistant sends the command once and assumes success. This integration verifies that entities actually reached the target state and retries if they didn't.

This solves the common problem of lights occasionally missing commands due to network congestion, Zigbee/Z-Wave mesh issues, or unresponsive devices. Instead of building retry logic into every script and automation, HA Light Controller handles verification centrally with configurable tolerances and backoff strategies.

### How It Works

1. Sends the light command (on/off, brightness, color, etc.)
2. Waits a configurable delay for the state to update
3. Verifies entity attributes match target values within tolerance
4. Retries with exponential backoff if verification fails
5. Optionally logs success or sends failure notifications

## Key Features

- **State verification** - Confirms entities reached target brightness, color, and temperature within configurable tolerances
- **Automatic retries** - Configurable retry attempts with exponential backoff
- **Group expansion** - Automatically expands `light.*` and `group.*` entities to individual lights
- **Per-entity overrides** - Set different attributes for each light in a single service call via the `targets` parameter
- **Presets** - Store light configurations as button entities for one-tap activation
- **Failure notifications** - Send alerts via any `notify.*` service when verification fails
- **Blueprints** - Pre-built automation templates for common patterns

## Installation

### HACS

1. Add `https://github.com/L3DigitalNet/HA-Light-Controller` as a custom repository (Integration)
2. Install "HA Light Controller"
3. Restart Home Assistant

### Manual

1. Copy `custom_components/ha_light_controller` to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

Add the integration via **Settings** → **Devices & Services** → **Add Integration** → "Light Controller".

Configuration options include default brightness, transition time, verification tolerances (brightness, RGB, Kelvin), retry settings, and notification services.

## Usage

### Basic Service Call

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
  state: "off"
  notify_on_failure: "notify.mobile_app_phone"
```

### Per-Entity Overrides

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.ceiling
    - light.lamp
  brightness_pct: 50
  targets:
    - entity_id: light.ceiling
      brightness_pct: 100
      color_temp_kelvin: 4000
    - entity_id: light.lamp
      brightness_pct: 30
      rgb_color: [255, 200, 150]
```

### Presets

Create presets via the integration options or programmatically:

```yaml
service: ha_light_controller.create_preset
data:
  name: "Movie Night"
  entities:
    - light.living_room
    - light.tv_backlight
  brightness_pct: 20
  color_temp_kelvin: 2700
```

Each preset creates a `button.*` entity for activation and a `sensor.*` entity for status tracking.

## Blueprints

Included automation blueprints (available in **Settings** → **Automations & Scenes** → **Blueprints**):

| Blueprint | Description |
| --------- | ----------- |
| Motion-Activated Scene | Trigger lights on motion with configurable timeout |
| Button Scene Controller | Map button events to up to 4 light scenes |
| Scene Scheduler | Time-based scene activation with day/presence conditions |
| Adaptive Lighting | Sun-position-based color temperature and brightness |

## Documentation

See the **[Usage Guide](USAGE.md)** for complete service parameters, configuration options, and examples.

## Links

- [Issue Tracker](https://github.com/L3DigitalNet/HA-Light-Controller/issues)
- [License (MIT)](LICENSE)
