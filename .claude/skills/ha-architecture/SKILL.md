---
name: ha-architecture
description: Explain Home Assistant core architecture including the event bus, state machine, service registry, and how integrations hook into them. Use when the user asks about HA internals, event propagation, state management, entity lifecycle, hass object, or how integrations interact with the HA core. Also triggers on "event bus", "state machine", "state_changed", "hass object", "entity registry", "device registry", or questions about how Home Assistant works under the hood.
---

# Home Assistant Core Architecture

## The hass Object

Every integration receives a `HomeAssistant` instance (`hass`). This is the central hub providing access to all core systems. Never store global state outside of it.

```python
from homeassistant.core import HomeAssistant

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # hass.bus       — event bus
    # hass.states    — state machine
    # hass.services  — service registry
    # hass.data      — shared data store (prefer entry.runtime_data for new code)
    # hass.config    — system configuration (location, units, etc.)
    ...
```

## Event Bus

The event bus is the nervous system of Home Assistant. All communication between components flows through events.

```python
# Firing an event
hass.bus.async_fire("my_custom_event", {"key": "value"})

# Listening for events (use @callback for sync handlers, no I/O allowed)
from homeassistant.core import callback, Event

@callback
def handle_event(event: Event) -> None:
    """Handle event (must be non-blocking)."""
    entity_id = event.data.get("entity_id")
    new_state = event.data.get("new_state")

unsub = hass.bus.async_listen("state_changed", handle_event)

# Always clean up listeners on unload
entry.async_on_unload(unsub)
```

Key built-in events: `state_changed` (entity state updates), `service_registered`, `homeassistant_start`, `homeassistant_stop`, `automation_triggered`, `call_service`, `component_loaded`.

Event listeners decorated with `@callback` run on the event loop and must NOT perform I/O. If you need async work, schedule a task from within the callback.

## State Machine

The state machine tracks the current state of every entity. States are immutable snapshots: reading a state gives you a point-in-time value that won't change.

```python
# Reading state
state = hass.states.get("sensor.temperature")
if state is not None:
    value = state.state          # String value ("22.5", "on", "unavailable")
    attrs = state.attributes     # Dict of attributes
    last_changed = state.last_changed
    last_updated = state.last_updated

# Setting state directly (rarely needed — entities do this automatically)
hass.states.async_set("sensor.my_sensor", "42", {"unit_of_measurement": "°C"})
```

Important: `state.state` is always a string. The special values `"unavailable"` and `"unknown"` indicate entity issues. When an entity is unavailable, its coordinator has failed or the device is offline.

## Service Registry

Services are named actions that entities and integrations expose. They are the primary mechanism for controlling devices.

```python
# Registering a service
async def handle_my_service(call: ServiceCall) -> None:
    """Handle the service call."""
    target_entities = call.data.get("entity_id")
    value = call.data.get("value")
    await do_something(target_entities, value)

hass.services.async_register(
    DOMAIN,
    "my_action",
    handle_my_service,
    schema=vol.Schema({
        vol.Required("entity_id"): cv.entity_ids,
        vol.Optional("value", default=100): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=255)
        ),
    }),
)

# Calling a service
await hass.services.async_call(
    "light", "turn_on",
    {"entity_id": "light.living_room", "brightness": 200},
    blocking=True,
)
```

## Entity Lifecycle

Entities go through a defined lifecycle managed by Home Assistant:

1. **Platform discovery**: `async_setup_entry` on the platform module is called
2. **Entity creation**: Entity objects are instantiated and passed to `async_add_entities`
3. **Registration**: HA assigns entity_id, registers in entity registry
4. **First update**: `async_added_to_hass` is called, then initial state is written
5. **Ongoing updates**: Coordinator triggers `_handle_coordinator_update`, entity writes state
6. **Removal**: `async_will_remove_from_hass` is called for cleanup

```python
class MyEntity(CoordinatorEntity):
    async def async_added_to_hass(self) -> None:
        """Called when entity is added to HA (restore state, subscribe to extras)."""
        await super().async_added_to_hass()
        # Restore previous state if needed
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_native_value = last_state.state

    async def async_will_remove_from_hass(self) -> None:
        """Called when entity is being removed (cleanup resources)."""
        await super().async_will_remove_from_hass()
```

## Device and Entity Registries

The device registry groups entities under physical or logical devices. The entity registry tracks entity_id assignments and user customizations.

```python
from homeassistant.helpers.device_registry import DeviceInfo

# DeviceInfo groups entities into a device in the UI
@property
def device_info(self) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, self._serial)},  # Stable, unique tuple
        name="My Device",
        manufacturer="Acme",
        model="Widget Pro",
        sw_version="1.2.3",
        hw_version="rev2",
        configuration_url="http://192.168.1.100",
    )
```

`identifiers` must be a set of `(domain, unique_value)` tuples that remain stable across restarts. This is how HA knows two entities belong to the same device.

## Integration Loading Order

1. Home Assistant core starts, loads `configuration.yaml`
2. Dependencies listed in `manifest.json` are loaded first
3. `async_setup(hass, config)` is called (if present) for global setup
4. For each config entry: `async_setup_entry(hass, entry)` is called
5. Platform forwarding loads each platform's `async_setup_entry`
6. Entities are registered and begin receiving updates

## Key Design Principles

The event loop is single-threaded. All code on the main thread shares one asyncio loop. Blocking it freezes the entire system. Use `await hass.async_add_executor_job()` for any synchronous I/O.

State is immutable. When you read `hass.states.get()`, you get a frozen snapshot. The state machine creates new State objects on each update rather than mutating existing ones.

Integrations are isolated. Each integration manages its own lifecycle through config entries. The `runtime_data` attribute on a config entry is the correct place to store integration-specific objects like coordinators and API clients.
