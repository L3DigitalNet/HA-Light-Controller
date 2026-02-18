HA Light Controller adds state verification and automatic retries to light commands.
When you call `light.turn_on`, Home Assistant sends the command once and assumes
success. This integration verifies that entities actually reached the target state and
retries if they didn't.

This solves the common problem of lights occasionally missing commands due to network
congestion, Zigbee/Z-Wave mesh issues, or unresponsive devices. Instead of building
retry logic into every script and automation, HA Light Controller handles verification
centrally with configurable tolerances and backoff strategies.

## How It Works

1. Sends the light command (on/off, brightness, color, etc.)
2. Waits a configurable delay for the state to update
3. Verifies entity attributes match target values within tolerance
4. Retries with exponential backoff if verification fails
5. Optionally logs success to the Home Assistant logbook

## Key Features

- **State verification** - Confirms entities reached target brightness, color, and
  temperature within configurable tolerances
- **Automatic retries** - Configurable retry attempts with exponential backoff
- **Group expansion** - Automatically expands `light.*` and `group.*` entities to
  individual lights
- **Per-entity overrides** - Set different attributes for each light in a single service
  call via the `targets` parameter
- **Presets** - Store light configurations as button entities for one-tap activation

## Quick Start

```yaml
service: ha_light_controller.ensure_state
data:
  entities:
    - light.living_room_ceiling
    - light.living_room_lamp
  brightness_pct: 80
  color_temp_kelvin: 3000
```

## Services

| Service | Description |
|---|---|
| `ensure_state` | Control lights with verification and retries |
| `activate_preset` | Activate a saved preset by name or ID |
| `create_preset` | Create a preset programmatically |
| `create_preset_from_current` | Capture current light states as a preset |
| `delete_preset` | Delete a preset by ID |
