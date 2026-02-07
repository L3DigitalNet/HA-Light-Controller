---
name: ha-service-calls
description: Generate and explain Home Assistant service calls for controlling entities (lights, switches, climate, media, covers, etc.) in both Python and YAML. Use when the user asks about calling services, controlling devices, "hass.services.async_call", entity actions, "turn_on", "turn_off", "set_temperature", or needs to invoke HA services from Python code or automations.
---

# Home Assistant Service Calls

Service calls are the primary mechanism for controlling devices in Home Assistant. They can be invoked from Python code within integrations, from automations and scripts in YAML, and from the Developer Tools UI.

## Python Service Calls

### Basic Pattern

```python
await hass.services.async_call(
    domain="light",
    service="turn_on",
    service_data={"brightness_pct": 80, "color_temp_kelvin": 3000},
    target={"entity_id": "light.living_room"},
    blocking=True,  # Wait for completion
)
```

Set `blocking=True` when you need to ensure the action completes before proceeding. Set `blocking=False` (the default) for fire-and-forget calls.

### Targeting Multiple Entities

```python
# Multiple specific entities
await hass.services.async_call(
    "light", "turn_off",
    target={"entity_id": ["light.kitchen", "light.hallway"]},
    blocking=True,
)

# Target by area
await hass.services.async_call(
    "light", "turn_on",
    target={"area_id": "living_room"},
    blocking=True,
)

# Target by device
await hass.services.async_call(
    "switch", "turn_off",
    target={"device_id": "abc123def456"},
    blocking=True,
)
```

### Registering Custom Services

```python
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register custom services."""

    async def handle_set_mode(call: ServiceCall) -> None:
        """Handle the set_mode service call."""
        entity_id = call.data["entity_id"]
        mode = call.data["mode"]

        # Get the entity from the platform
        component = hass.data.get("entity_components", {}).get(DOMAIN)
        if component:
            entity = component.get_entity(entity_id)
            if entity:
                await entity.async_set_mode(mode)

    hass.services.async_register(
        DOMAIN,
        "set_mode",
        handle_set_mode,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("mode"): vol.In(["auto", "manual", "eco"]),
        }),
    )
    return True
```

### Service Descriptions (services.yaml)

Define service metadata for the UI:

```yaml
# services.yaml
set_mode:
  name: "Set Mode"
  description: "Set the operating mode of the device."
  target:
    entity:
      integration: my_integration
  fields:
    mode:
      name: "Mode"
      description: "The operating mode to set."
      required: true
      example: "auto"
      selector:
        select:
          options:
            - "auto"
            - "manual"
            - "eco"
```

## Common Service Calls Reference

### Lights

```python
# Turn on with brightness and color
await hass.services.async_call("light", "turn_on", {
    "entity_id": "light.bedroom",
    "brightness_pct": 80,           # 0-100 percentage
    "color_temp_kelvin": 3000,      # Warm white
})

# Turn on with RGB color
await hass.services.async_call("light", "turn_on", {
    "entity_id": "light.accent",
    "rgb_color": [255, 0, 100],     # RGB tuple
    "brightness": 200,               # 0-255 raw value
    "transition": 2,                 # Fade duration in seconds
})

# Toggle
await hass.services.async_call("light", "toggle", {
    "entity_id": "light.bedroom",
})
```

### Climate

```python
# Set temperature
await hass.services.async_call("climate", "set_temperature", {
    "entity_id": "climate.thermostat",
    "temperature": 22,
    "hvac_mode": "heat",
})

# Set HVAC mode
await hass.services.async_call("climate", "set_hvac_mode", {
    "entity_id": "climate.thermostat",
    "hvac_mode": "cool",  # off, heat, cool, heat_cool, auto, dry, fan_only
})
```

### Media Player

```python
# Play media
await hass.services.async_call("media_player", "play_media", {
    "entity_id": "media_player.speaker",
    "media_content_id": "https://example.com/stream",
    "media_content_type": "music",
})

# Set volume
await hass.services.async_call("media_player", "volume_set", {
    "entity_id": "media_player.speaker",
    "volume_level": 0.5,  # 0.0 to 1.0
})
```

### Covers

```python
# Set position
await hass.services.async_call("cover", "set_cover_position", {
    "entity_id": "cover.blinds",
    "position": 50,  # 0 = closed, 100 = open
})
```

### Notifications

```python
await hass.services.async_call("notify", "mobile_app_phone", {
    "message": "Motion detected in the garage",
    "title": "Security Alert",
    "data": {"priority": "high"},
})
```

## YAML Service Calls (In Automations)

The YAML equivalent uses `action:` in automations and scripts:

```yaml
action:
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp_kelvin: 3000

  - action: climate.set_temperature
    target:
      entity_id: climate.thermostat
    data:
      temperature: 22

  - action: notify.mobile_app_phone
    data:
      message: "Temperature is {{ states('sensor.temperature') }}°C"
      title: "Climate Update"
```

## Entity Service Registration (For Platform Entities)

When your entity platform needs services that operate on specific entities:

```python
from homeassistant.helpers import entity_platform

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the platform with entity services."""
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_mode",
        {vol.Required("mode"): vol.In(["auto", "manual", "eco"])},
        "async_set_mode",  # Method name on the entity class
    )

    async_add_entities([MyEntity(entry.runtime_data)])
```

## Key Rules

Always use `blocking=True` when subsequent logic depends on the service completing. Use `target` for entity/area/device targeting instead of putting `entity_id` in `service_data`. Service names use underscores in Python and dots in YAML (e.g., Python `"turn_on"` maps to YAML `light.turn_on`). Register services in `async_setup` for domain-level services or use `entity_platform.async_register_entity_service` for entity-specific services.
