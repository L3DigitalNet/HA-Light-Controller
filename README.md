# Light Controller

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/L3DigitalNet/HA-Light-Controller.svg)](https://github.com/L3DigitalNet/HA-Light-Controller/releases)
[![License](https://img.shields.io/github/license/L3DigitalNet/HA-Light-Controller.svg)](LICENSE)

A powerful Home Assistant custom integration for reliable light control with state verification, automatic retries, and preset management.

## Features

- **State Verification**: Confirms lights actually reach the target state after commands
- **Automatic Retries**: Configurable retry logic with exponential backoff
- **Group Expansion**: Automatically expands light groups and helper groups to individual lights
- **Per-Light Overrides**: Set different brightness, color, or temperature for each light
- **Tolerance Settings**: Configurable thresholds for brightness, RGB, and color temperature verification
- **Presets**: Save and activate light scenes with button entities
- **Fire-and-Forget Mode**: Option to skip verification for faster execution
- **Failure Notifications**: Get notified when lights fail to reach target state
- **Blueprints**: Pre-built automation templates for common scenarios

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/L3DigitalNet/HA-Light-Controller` as an Integration
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Download the `light_controller` folder from the `custom_components` directory
2. Copy it to your Home Assistant's `custom_components` folder
3. Restart Home Assistant

## Configuration

After installation, add the integration via the UI:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Light Controller"
4. Follow the setup wizard to configure default settings

### Options

Access options via the integration's **Configure** button:

| Category | Settings |
|----------|----------|
| **Default Settings** | Default brightness, transition time |
| **Verification Tolerances** | Brightness, RGB, and Kelvin tolerance thresholds |
| **Retry & Timing** | Delay after send, max retries, timeout, exponential backoff |
| **Logging & Notifications** | Success logging, failure notification service |
| **Presets** | Add, manage, and delete light presets |

## Services

### `light_controller.ensure_state`

The main service for controlling lights with verification.

```yaml
service: light_controller.ensure_state
data:
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
  state: "on"
  brightness_pct: 75
  color_temp_kelvin: 3000
  transition: 2
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entities` | list | Yes | Light entities, light groups, or helper groups |
| `state` | string | No | Target state: `on` or `off` (default: `on`) |
| `brightness_pct` | int | No | Brightness percentage (1-100) |
| `rgb_color` | list | No | RGB color as [R, G, B] |
| `color_temp_kelvin` | int | No | Color temperature in Kelvin |
| `effect` | string | No | Effect name to apply |
| `targets` | list | No | Per-light override settings |
| `transition` | float | No | Transition time in seconds |
| `skip_verification` | bool | No | Skip state verification (fire-and-forget) |
| `brightness_tolerance` | int | No | Override brightness tolerance |
| `rgb_tolerance` | int | No | Override RGB tolerance |
| `kelvin_tolerance` | int | No | Override Kelvin tolerance |
| `delay_after_send` | float | No | Override delay before verification |
| `max_retries` | int | No | Override maximum retry attempts |
| `max_runtime_seconds` | int | No | Override hard timeout |
| `use_exponential_backoff` | bool | No | Override backoff setting |
| `max_backoff_seconds` | int | No | Override maximum backoff delay |
| `log_success` | bool | No | Log success to logbook |
| `notify_on_failure` | string | No | Notification service for failures |

#### Per-Light Overrides

Use the `targets` parameter to set different values for each light:

```yaml
service: light_controller.ensure_state
data:
  entities:
    - light.ceiling
    - light.lamp
    - light.accent
  state: "on"
  brightness_pct: 50  # Default for all lights
  targets:
    - entity_id: light.ceiling
      brightness_pct: 100
      color_temp_kelvin: 4000
    - entity_id: light.lamp
      brightness_pct: 30
      rgb_color: [255, 200, 150]
    - entity_id: light.accent
      brightness_pct: 75
      effect: "colorloop"
```

### `light_controller.activate_preset`

Activate a saved preset by name or ID.

```yaml
service: light_controller.activate_preset
data:
  preset: "Evening Mode"
```

### `light_controller.create_preset`

Create a new preset programmatically.

```yaml
service: light_controller.create_preset
data:
  name: "Movie Night"
  entities:
    - light.living_room_ceiling
    - light.tv_backlight
  state: "on"
  brightness_pct: 20
  color_temp_kelvin: 2700
  transition: 3
```

### `light_controller.create_preset_from_current`

Capture the current state of lights as a new preset.

```yaml
service: light_controller.create_preset_from_current
data:
  name: "Current Scene"
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
```

### `light_controller.delete_preset`

Delete a preset by its ID.

```yaml
service: light_controller.delete_preset
data:
  preset_id: "abc123-def456"
```

## Presets

Presets are saved light configurations that can be activated with a single tap. Each preset creates:

- **Button Entity**: Press to activate the preset
- **Status Sensor**: Shows idle, activating, success, or failed

### Creating Presets via UI

1. Go to the integration's options
2. Select **Add New Preset**
3. Configure the preset settings
4. The button and sensor entities are created automatically

### Using Preset Buttons

Add preset buttons to your dashboard:

```yaml
type: button
entity: button.light_controller_evening_mode
tap_action:
  action: toggle
```

Or use in automations:

```yaml
automation:
  - alias: "Sunset Scene"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: button.press
        target:
          entity_id: button.light_controller_evening_mode
```

## Blueprints

The integration includes pre-built automation blueprints:

### Motion-Activated Scene

Activates a scene when motion is detected with optional timeout.

**Inputs:**
- Motion sensor entity
- Target lights
- Brightness and color settings
- No-motion timeout
- Time conditions

### Button Scene Controller

Maps button or remote events to up to 4 different scenes.

**Inputs:**
- Button device
- Scene configurations for each button

### Scene Scheduler

Activates scenes based on time of day.

**Inputs:**
- Trigger time
- Target lights
- Scene settings
- Day-of-week conditions
- Optional presence condition

### Adaptive Lighting

Adjusts color temperature and brightness based on sun position.

**Inputs:**
- Target lights
- Min/max color temperature
- Min/max brightness
- Update interval

### Installing Blueprints

Blueprints are located in:
```
custom_components/light_controller/blueprints/automation/light_controller/
```

To use them:
1. Go to **Settings** → **Automations & Scenes** → **Blueprints**
2. The Light Controller blueprints should appear automatically
3. Click a blueprint and configure the inputs

## Example Automations

### Scene Script with Verification

```yaml
script:
  living_room_evening:
    alias: "Living Room Evening"
    sequence:
      - service: light_controller.ensure_state
        data:
          entities:
            - light.living_room_ceiling
            - light.floor_lamp
            - light.accent_lights
          state: "on"
          brightness_pct: 40
          color_temp_kelvin: 2700
          transition: 2
          targets:
            - entity_id: light.accent_lights
              rgb_color: [255, 180, 100]
              brightness_pct: 30
```

### Bedtime Routine with Notification

```yaml
automation:
  - alias: "Bedtime Lights"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: light_controller.ensure_state
        data:
          entities:
            - group.all_lights
          state: "off"
          notify_on_failure: "notify.mobile_app_phone"
          log_success: true
```

### Quick Fire-and-Forget

For situations where speed matters more than verification:

```yaml
service: light_controller.ensure_state
data:
  entities:
    - light.hallway
  state: "on"
  brightness_pct: 100
  skip_verification: true
```

## Troubleshooting

### Lights Not Reaching Target State

1. **Increase tolerances**: Some lights report slightly different values than set
2. **Increase delay_after_send**: Give lights more time before verification
3. **Check max_retries**: Increase retry attempts for unreliable lights
4. **Enable debug logging**:

```yaml
logger:
  default: info
  logs:
    custom_components.light_controller: debug
```

### Verification Always Fails

- Check that the light supports the attribute you're setting (e.g., not all lights support RGB)
- Verify the light is available and responding
- Increase tolerance values in the integration options

### Presets Not Appearing

- Restart Home Assistant after creating presets via the options flow
- Check the integration's entities for the button and sensor

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Report Issues](https://github.com/L3DigitalNet/HA-Light-Controller/issues)
- [Feature Requests](https://github.com/L3DigitalNet/HA-Light-Controller/issues)
