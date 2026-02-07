---
name: ha-async-patterns
description: Write correct async Python code for Home Assistant integrations. Use when the user mentions "async", "await", "event loop", "blocking", "executor", "async_add_executor_job", "coroutine", or asks about performance, non-blocking code, or async patterns in Home Assistant context.
---

# Async Python Patterns in Home Assistant

Home Assistant runs on a single-threaded asyncio event loop. **All I/O operations must be non-blocking.** Blocking the event loop freezes the entire system — automations stop, the UI becomes unresponsive, and entities stop updating.

## The Cardinal Rule

Never perform blocking I/O in an async function. This includes HTTP requests with `requests`, file I/O, DNS lookups, or any call that waits for external resources.

## Pattern 1: Async Libraries (Preferred)

Use async-native libraries whenever possible:

```python
import aiohttp

async def async_get_data(self) -> dict:
    """Fetch data using async HTTP client."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{self._host}/api/data") as response:
            response.raise_for_status()
            return await response.json()
```

## Pattern 2: Wrapping Sync Libraries

When no async library exists, use `hass.async_add_executor_job()`:

```python
import requests

async def async_get_data(self) -> dict:
    """Fetch data by running sync code in executor."""
    return await self.hass.async_add_executor_job(self._sync_get_data)

def _sync_get_data(self) -> dict:
    """Sync method that runs in executor thread."""
    response = requests.get(f"http://{self._host}/api/data", timeout=10)
    response.raise_for_status()
    return response.json()
```

For methods with arguments:

```python
# Pass positional arguments after the callable
result = await hass.async_add_executor_job(
    requests.get, f"http://{host}/api", {"timeout": 10}
)

# For keyword arguments, use functools.partial
from functools import partial
result = await hass.async_add_executor_job(
    partial(requests.get, url, timeout=10, headers=headers)
)
```

## Pattern 3: Setup Functions

Integration setup must be async:

```python
# __init__.py
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry (ASYNC REQUIRED)."""
    # All I/O here must be awaited
    coordinator = MyCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry (ASYNC REQUIRED)."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

## Pattern 4: Service Actions

Register services in `async_setup` (not `async_setup_entry`):

```python
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration."""

    async def handle_my_service(call: ServiceCall) -> None:
        """Handle the service call."""
        entity_id = call.data.get("entity_id")
        value = call.data.get("value")
        # Do async work here
        await some_async_operation(entity_id, value)

    hass.services.async_register(DOMAIN, "my_action", handle_my_service)
    return True
```

## Pattern 5: Event Listeners

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up with event listener."""

    @callback
    def handle_event(event: Event) -> None:
        """Handle a Home Assistant event (MUST be non-blocking)."""
        # @callback functions run on the event loop
        # Do NOT do I/O here — schedule async work instead
        hass.async_create_task(async_process_event(event))

    async def async_process_event(event: Event) -> None:
        """Process event asynchronously."""
        await some_async_work(event.data)

    # Register listener and store unsubscribe function
    unsub = hass.bus.async_listen("state_changed", handle_event)
    entry.async_on_unload(unsub)  # Auto-cleanup on unload
    return True
```

## Pattern 6: Callbacks vs Coroutines

```python
from homeassistant.core import callback

# @callback = synchronous function that's safe to call from event loop
# MUST NOT do any I/O or blocking work
@callback
def _handle_coordinator_update(self) -> None:
    """Update entity state from coordinator (synchronous, no I/O)."""
    self._attr_native_value = self.coordinator.data.get("value")
    self.async_write_ha_state()

# async = coroutine that CAN do I/O
async def async_turn_on(self, **kwargs) -> None:
    """Turn on the device (can do I/O)."""
    await self.coordinator.client.async_set_state(True)
    await self.coordinator.async_request_refresh()
```

## Pattern 7: Timeouts

Always use timeouts for external calls:

```python
import asyncio

async def async_get_data(self) -> dict:
    """Fetch with timeout."""
    try:
        async with asyncio.timeout(10):
            return await self.client.async_get_data()
    except TimeoutError:
        raise UpdateFailed("Request timed out")
```

## Common Mistakes and Fixes

**Blocking the event loop:**
```python
# WRONG - blocks the entire event loop
data = requests.get(url)
time.sleep(5)
open("file.txt").read()

# RIGHT
data = await hass.async_add_executor_job(requests.get, url)
await asyncio.sleep(5)
data = await hass.async_add_executor_job(Path("file.txt").read_text)
```

**Mixing sync and async:**
```python
# WRONG - calling sync method from async context
def get_data(self):  # sync method
    return requests.get(url)

async def _async_update_data(self):
    return self.get_data()  # Still blocks!

# RIGHT
async def _async_update_data(self):
    return await self.hass.async_add_executor_job(self.get_data)
```

**Creating tasks incorrectly:**
```python
# WRONG - task may be garbage collected
asyncio.create_task(my_coroutine())

# RIGHT - use HA's task management
hass.async_create_task(my_coroutine())
# Or for background tasks:
entry.async_create_background_task(hass, my_coroutine(), "task_name")
```
