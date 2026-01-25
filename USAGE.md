# HA Light Controller Usage Guide

Complete reference for services, configuration options, and examples.

## Table of Contents

- [Configuration Options](#configuration-options)
- [Services](#services)
  - [ensure_state](#ha_light_controllerensure_state)
  - [activate_preset](#ha_light_controlleractivate_preset)
  - [create_preset](#ha_light_controllercreate_preset)
  - [create_preset_from_current](#ha_light_controllercreate_preset_from_current)
  - [delete_preset](#ha_light_controllerdelete_preset)
- [Working with Presets](#working-with-presets)
- [Blueprints](#blueprints)
- [Example Automations](#example-automations)
- [Troubleshooting](#troubleshooting)

---

## Configuration Options

Access configuration options by going to **Settings** → **Devices & Services** → **Light Controller** → **Configure** → **Settings**.

All configuration options are available on a single settings page.

### Default Settings

| Setting | Description |
| ------- | ----------- |
| Default brightness | Brightness percentage used when not specified in a command (1-100) |
| Transition time | Default transition duration in seconds |

### Verification Tolerances

These settings control how precisely lights must match the target values to be considered successful.

| Setting | Description |
| ------- | ----------- |
| Brightness tolerance | Acceptable difference in brightness percentage (e.g., 5 means 45-55% is acceptable when 50% is requested) |
| RGB tolerance | Acceptable difference in each RGB color channel (0-255 scale) |
| Kelvin tolerance | Acceptable difference in color temperature (Kelvin) |

### Retry & Timing

| Setting | Description |
| ------- | ----------- |
| Delay after send | Seconds to wait after sending a command before checking the result |
| Max retries | Maximum number of retry attempts if a light doesn't respond |
| Timeout | Maximum total time allowed for the entire operation |
| Exponential backoff | Gradually increase delay between retries (recommended for congested networks) |
| Max backoff | Maximum delay between retries when using exponential backoff |

### Logging & Notifications

| Setting | Description |
| ------- | ----------- |
| Log success | Write successful operations to the Home Assistant logbook |
| Failure notification | Notification service to call when lights fail to respond (e.g., `notify.mobile_app_phone`) |

---

## Services

### ha_light_controller.ensure_state

Primary service for controlling lights with state verification and automatic retries.

#### Basic Example

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
  state: "on"
  brightness_pct: 75
  color_temp_kelvin: 3000
  transition: 2
```

#### All Parameters

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `entities` | list | Yes | Light entities, light groups, or helper groups to control |
| `state` | string | No | Target state: `on` or `off` (default: `on`) |
| `brightness_pct` | int | No | Brightness percentage (1-100) |
| `rgb_color` | list | No | RGB color as `[R, G, B]` (each value 0-255) |
| `color_temp_kelvin` | int | No | Color temperature in Kelvin (e.g., 2700 for warm, 6500 for cool) |
| `effect` | string | No | Effect name to apply (device-specific) |
| `targets` | list | No | Per-light override settings (see below) |
| `transition` | float | No | Transition time in seconds |
| `skip_verification` | bool | No | Skip state verification for faster execution |
| `brightness_tolerance` | int | No | Override configured brightness tolerance |
| `rgb_tolerance` | int | No | Override configured RGB tolerance |
| `kelvin_tolerance` | int | No | Override configured Kelvin tolerance |
| `delay_after_send` | float | No | Override configured delay before verification |
| `max_retries` | int | No | Override configured retry attempts |
| `max_runtime_seconds` | float | No | Override configured timeout |
| `use_exponential_backoff` | bool | No | Override configured backoff setting |
| `max_backoff_seconds` | float | No | Override configured maximum backoff delay |
| `log_success` | bool | No | Log success to logbook |
| `notify_on_failure` | string | No | Notification service to call on failure |

#### Per-Light Overrides

Use `targets` to override settings for specific entities. Entities not in `targets` use the top-level defaults.

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.ceiling
    - light.lamp
    - light.accent
  state: "on"
  brightness_pct: 50  # Default for entities not in targets
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

---

### ha_light_controller.activate_preset

Activate a saved preset by its name or ID.

```yaml
service: ha_light_controller.activate_preset
data:
  preset: "Evening Mode"
```

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `preset` | string | Yes | Preset name or ID |

---

### ha_light_controller.create_preset

Create a new preset programmatically via a service call.

```yaml
service: ha_light_controller.create_preset
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

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `name` | string | Yes | Name for the preset |
| `entities` | list | Yes | Light entities to include |
| `state` | string | No | Target state: `on` or `off` |
| `brightness_pct` | int | No | Brightness percentage |
| `rgb_color` | list | No | RGB color as `[R, G, B]` |
| `color_temp_kelvin` | int | No | Color temperature in Kelvin |
| `effect` | string | No | Effect to apply |
| `targets` | list | No | Per-light overrides (same format as `ensure_state`) |
| `transition` | float | No | Transition time in seconds |
| `skip_verification` | bool | No | Use fire-and-forget mode for this preset |

---

### ha_light_controller.create_preset_from_current

Captures current state of specified lights and saves as a new preset.

```yaml
service: ha_light_controller.create_preset_from_current
data:
  name: "Current Scene"
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
```

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `name` | string | Yes | Name for the new preset |
| `entities` | list | Yes | Light entities to capture |

---

### ha_light_controller.delete_preset

Delete a preset by its ID.

```yaml
service: ha_light_controller.delete_preset
data:
  preset_id: "abc123-def456"
```

| Parameter | Type | Required | Description |
| --------- | ---- | -------- | ----------- |
| `preset_id` | string | Yes | The unique ID of the preset to delete |

---

## Working with Presets

Each preset creates two entities:

- `button.ha_light_controller_<preset_name>` - Activates the preset when pressed
- `sensor.ha_light_controller_<preset_name>_status` - Shows activation status

### Preset Button

The button entity displays a dynamic icon based on the preset's target state:

- `mdi:lightbulb-group` for presets that turn lights **on**
- `mdi:lightbulb-group-off` for presets that turn lights **off**

**Attributes:**

| Attribute | Description |
| --------- | ----------- |
| `preset_id` | Unique identifier for the preset |
| `entities` | List of target light entities |
| `state` | Target state (`on` or `off`) |
| `brightness_pct` | Target brightness percentage |
| `rgb_color` | RGB color (if set) |
| `color_temp_kelvin` | Color temperature (if set) |
| `last_result` | Result of the last activation (`success` or `failed`) |
| `last_activated` | Timestamp of last activation |

### Preset Status Sensor

Shows the current activation status with dynamic icons:

| State | Icon | Description |
| ----- | ---- | ----------- |
| Idle | `mdi:lightbulb-outline` | Preset is ready to activate |
| Activating... | `mdi:lightbulb-on` | Preset is currently being applied |
| Success | `mdi:lightbulb-on-outline` | All lights reached target state |
| Failed | `mdi:lightbulb-alert` | Some lights failed verification |

**Attributes:**

| Attribute | Description |
| --------- | ----------- |
| `preset_id` | Unique identifier for the preset |
| `preset_name` | Display name of the preset |
| `target_state` | Target state (`on` or `off`) |
| `entity_count` | Number of lights in the preset |
| `last_activated` | Timestamp of last activation |
| `last_success` | Whether last activation succeeded |
| `last_message` | Status message from last activation |
| `last_attempts` | Number of retry attempts used |
| `last_elapsed` | Time taken (e.g., `"1.2s"`) |
| `failed_lights` | List of lights that failed (if any) |
| `failed_count` | Count of failed lights |
| `skipped_lights` | List of skipped lights (if any) |
| `skipped_count` | Count of skipped lights |

### Creating Presets via UI

**Settings** → **Devices & Services** → **Light Controller** → **Configure** → **Add New Preset**

The preset creation flow supports per-entity configuration:

1. **Basic Settings** - Enter preset name, select entities, optionally skip verification
2. **Entity Hub** - Manage entities and their configurations:
   - **Configure an entity** - Set state, brightness, color, and transition for each light individually
   - **Add more entities** - Include additional lights
   - **Remove an entity** - Remove lights from the preset (requires at least one)
   - **Save preset** - Finalize once at least one entity is configured

This allows presets where different lights have different settings (e.g., ceiling at 100% warm white, accent at 30% RGB red).

### Dashboard Cards

```yaml
type: button
entity: button.ha_light_controller_evening_mode
tap_action:
  action: toggle
```

```yaml
type: entities
entities:
  - entity: button.ha_light_controller_evening_mode
  - entity: sensor.ha_light_controller_evening_mode_status
```

### Using Presets in Automations

Via button entity:

```yaml
service: button.press
target:
  entity_id: button.ha_light_controller_evening_mode
```

Via service:

```yaml
service: ha_light_controller.activate_preset
data:
  preset: "Evening Mode"
```

---

## Blueprints

Located in **Settings** → **Automations & Scenes** → **Blueprints**.

### Motion-Activated Scene

Triggers lights on motion detection with configurable timeout.

**Inputs:** Motion sensor, target lights, brightness/color settings, timeout duration, time conditions

### Button Scene Controller

Maps button/remote events to up to 4 light scenes.

**Inputs:** Button device, scene configurations per action (single press, double press, etc.)

### Scene Scheduler

Time-based scene activation with day-of-week and presence conditions.

**Inputs:** Trigger time, target lights, scene settings, day/presence conditions

### Adaptive Lighting

Adjusts color temperature and brightness based on sun position.

**Inputs:** Target lights, min/max color temperature, min/max brightness, update interval

### Blueprint Location

```text
custom_components/ha_light_controller/blueprints/automation/ha_light_controller/
```

---

## Example Automations

### Script with Per-Light Overrides

```yaml
script:
  living_room_evening:
    alias: "Living Room Evening"
    sequence:
      - service: ha_light_controller.ensure_state
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

### Automation with Failure Notification

```yaml
automation:
  - alias: "Bedtime Lights"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: ha_light_controller.ensure_state
        data:
          entities:
            - group.all_lights
          state: "off"
          notify_on_failure: "notify.mobile_app_phone"
          log_success: true
```

### Skip Verification (Fire-and-Forget)

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.hallway
  state: "on"
  brightness_pct: 100
  skip_verification: true
```

### Gradual Brightness Increase

```yaml
automation:
  - alias: "Morning Wake Up"
    trigger:
      - platform: time
        at: "06:30:00"
    action:
      - service: ha_light_controller.ensure_state
        data:
          entities:
            - light.bedroom_ceiling
          state: "on"
          brightness_pct: 10
          color_temp_kelvin: 2700
          transition: 1
      - delay: "00:05:00"
      - service: ha_light_controller.ensure_state
        data:
          entities:
            - light.bedroom_ceiling
          brightness_pct: 50
          color_temp_kelvin: 4000
          transition: 300
      - delay: "00:05:00"
      - service: ha_light_controller.ensure_state
        data:
          entities:
            - light.bedroom_ceiling
          brightness_pct: 100
          color_temp_kelvin: 5500
          transition: 300
```

### Capture Current State as Preset

```yaml
script:
  save_current_lighting:
    alias: "Save Current Lighting"
    sequence:
      - service: ha_light_controller.create_preset_from_current
        data:
          name: "Saved Scene"
          entities:
            - light.living_room_ceiling
            - light.living_room_lamp
            - light.tv_backlight
```

---

## Troubleshooting

### Lights Not Reaching Target State

If lights frequently fail verification:

1. **Increase tolerances**: Some lights report slightly different values than what was set. Try increasing brightness tolerance to 5-10%.

2. **Increase delay_after_send**: Some lights take time to report their new state. Try 1-2 seconds.

3. **Increase max_retries**: For unreliable networks, try 5+ retries.

4. **Enable debug logging** to see exactly what's happening:

```yaml
logger:
  default: info
  logs:
    custom_components.ha_light_controller: debug
```

### Verification Always Fails for Specific Lights

- **Check capability**: Not all lights support all features. A light that doesn't support RGB will always fail RGB verification.
- **Check availability**: Ensure the light is powered on and connected to your network.
- **Check the reported state**: Use Developer Tools → States to see what values the light actually reports.

### Presets Not Appearing

- Restart Home Assistant after creating presets via the options flow.
- Check **Settings** → **Devices & Services** → **Light Controller** → **Entities** to see if the button and sensor were created.
- Look for errors in the Home Assistant log.

### Commands Are Slow

- Reduce `delay_after_send` if your lights respond quickly.
- Enable `skip_verification` for non-critical commands.
- Use groups instead of individual lights where possible (Light Controller will expand them automatically, but sending to a group can be faster).

### Getting "Entity not found" Errors

- Verify the entity ID is correct (check in Developer Tools → States).
- Make sure you're using the full entity ID (e.g., `light.living_room`, not just `living_room`).
- For groups, use either `light.group_name` or `group.group_name` depending on how the group was created.

---

## Links

- [GitHub Repository](https://github.com/L3DigitalNet/HA-Light-Controller)
- [Issue Tracker](https://github.com/L3DigitalNet/HA-Light-Controller/issues)
