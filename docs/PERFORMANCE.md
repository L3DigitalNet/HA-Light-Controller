# Performance Best Practices

This guide provides patterns and strategies to optimize Home Assistant integration performance, focusing on efficient data fetching, coordinator usage, and resource management.

## Table of Contents

- [DataUpdateCoordinator Optimization](#dataupdatecoordinator-optimization)
- [Update Interval Selection](#update-interval-selection)
- [Efficient Data Structures](#efficient-data-structures)
- [Entity Updates](#entity-updates)
- [Memory Management](#memory-management)
- [Async Best Practices](#async-best-practices)
- [Common Performance Anti-Patterns](#common-performance-anti-patterns)

---

## DataUpdateCoordinator Optimization

### ✅ DO: Use Single Coordinator Per Device/Service

```python
# ✅ CORRECT - One coordinator manages all data
class MyCoordinator(DataUpdateCoordinator):
    """Single coordinator for all device data."""

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data in one request."""
        return await self.api.fetch_all_data()


# In __init__.py
coordinator = MyCoordinator(hass, api_client)

# All platforms use same coordinator
hass.data[DOMAIN][entry.entry_id] = coordinator

await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
```

### ❌ DON'T: Create Multiple Coordinators

```python
# ❌ WRONG - Multiple coordinators = multiple API calls
class TemperatureCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        return await self.api.fetch_temperature()


class HumidityCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        return await self.api.fetch_humidity()


# DON'T DO THIS - Two API calls every update!
temp_coordinator = TemperatureCoordinator(...)
humidity_coordinator = HumidityCoordinator(...)
```

### Batch API Requests

```python
class MyCoordinator(DataUpdateCoordinator):
    """Coordinator that batches requests efficiently."""

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all device data in parallel."""
        # ✅ GOOD - Parallel requests for multiple devices
        devices = await asyncio.gather(
            *[self.api.fetch_device(device_id) for device_id in self.device_ids],
            return_exceptions=True,
        )

        # Handle individual failures gracefully
        result = {}
        for device_id, device_data in zip(self.device_ids, devices):
            if isinstance(device_data, Exception):
                _LOGGER.warning("Failed to fetch %s: %s", device_id, device_data)
                continue
            result[device_id] = device_data

        return result
```

---

## Update Interval Selection

### Choose Appropriate Intervals

| Device Type | Recommended Interval | Rationale |
|-------------|---------------------|-----------|
| Temperature sensors | 30-60 seconds | Temperature changes slowly |
| Energy monitors | 10-30 seconds | Real-time usage tracking |
| Light switches | Push updates | State changes via webhooks/callbacks |
| Weather data | 5-15 minutes | External API rate limits |
| Stock prices | 1-5 minutes | Market data doesn't change that fast |

### Dynamic Update Intervals

```python
from datetime import timedelta

class SmartCoordinator(DataUpdateCoordinator):
    """Coordinator with dynamic update intervals."""

    def __init__(self, hass: HomeAssistant):
        """Initialize with default interval."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),  # Default
        )

    def adjust_update_interval(self, device_state: str) -> None:
        """Adjust interval based on device state."""
        if device_state == "active":
            # More frequent updates when device is active
            self.update_interval = timedelta(seconds=10)
        elif device_state == "idle":
            # Less frequent when idle
            self.update_interval = timedelta(minutes=5)
        elif device_state == "sleeping":
            # Very infrequent when sleeping
            self.update_interval = timedelta(minutes=30)

        _LOGGER.debug("Update interval adjusted to %s", self.update_interval)
```

### Conditional Updates

Skip updates when not needed:

```python
class ConditionalCoordinator(DataUpdateCoordinator):
    """Coordinator that skips unnecessary updates."""

    def __init__(self, hass: HomeAssistant):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            always_update=False,  # Only update if data changed
        )
        self._last_hash = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data only if it changed."""
        data = await self.api.fetch_data()

        # Calculate hash of current data
        current_hash = hash(str(data))

        # Skip update if data unchanged
        if current_hash == self._last_hash:
            _LOGGER.debug("Data unchanged, skipping update")
            raise UpdateFailed("No changes")  # Prevents entity updates

        self._last_hash = current_hash
        return data
```

---

## Efficient Data Structures

### Use Immutable Data When Possible

```python
from typing import NamedTuple

# ✅ GOOD - Immutable, hashable, memory-efficient
class DeviceData(NamedTuple):
    """Device data structure."""
    device_id: str
    temperature: float
    humidity: float
    timestamp: datetime

# Coordinator returns immutable data
async def _async_update_data(self) -> dict[str, DeviceData]:
    """Return immutable device data."""
    return {
        device_id: DeviceData(**device_dict)
        for device_id, device_dict in raw_data.items()
    }
```

### Avoid Large Data in Memory

```python
# ❌ WRONG - Stores entire history in memory
class HistoryCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(...)
        self.history = []  # Grows indefinitely!

    async def _async_update_data(self):
        data = await self.api.fetch()
        self.history.append(data)  # Memory leak!
        return data


# ✅ CORRECT - Use HA's recorder or limit history
class EfficientCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(...)
        self._recent_data = deque(maxlen=100)  # Fixed size

    async def _async_update_data(self):
        data = await self.api.fetch()
        self._recent_data.append(data)  # Auto-discards old data
        return data
```

### Cache Computed Values

```python
from functools import lru_cache

class OptimizedEntity(CoordinatorEntity):
    """Entity with cached computed properties."""

    @property
    @lru_cache(maxsize=1)
    def native_value(self) -> float:
        """Cached computation."""
        # Expensive calculation only runs when data changes
        raw_value = self.coordinator.data[self.device_id]["value"]
        return self._complex_transformation(raw_value)

    def _handle_coordinator_update(self) -> None:
        """Clear cache when data updates."""
        self.native_value.ffi_cache_clear()  # Clear LRU cache
        super()._handle_coordinator_update()
```

---

## Entity Updates

### Use CoordinatorEntity

```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity

# ✅ CORRECT - Automatic updates from coordinator
class MySensor(CoordinatorEntity, SensorEntity):
    """Sensor that updates automatically."""

    @property
    def native_value(self):
        """Return value from coordinator data."""
        return self.coordinator.data[self.device_id]["value"]

    # Entity updates automatically when coordinator updates
```

### Avoid Manual Polling

```python
# ❌ WRONG - Manual polling in entity
class BadSensor(SensorEntity):
    async def async_update(self):
        """Fetch data in entity (anti-pattern!)."""
        self._value = await self.api.fetch()  # DON'T DO THIS


# ✅ CORRECT - Use coordinator
class GoodSensor(CoordinatorEntity, SensorEntity):
    @property
    def native_value(self):
        """Read from coordinator."""
        return self.coordinator.data[self.device_id]["value"]
```

### Minimize State Changes

```python
class EfficientSensor(CoordinatorEntity, SensorEntity):
    """Sensor that only updates when value changes."""

    @property
    def native_value(self) -> float | None:
        """Return value."""
        new_value = self.coordinator.data[self.device_id]["value"]

        # Round to reasonable precision
        return round(new_value, 2)  # Prevents updates from tiny changes

    @property
    def should_poll(self) -> bool:
        """Disable polling (uses coordinator)."""
        return False
```

---

## Memory Management

### Limit Stored History

```python
from collections import deque

class MemoryEfficientCoordinator(DataUpdateCoordinator):
    """Coordinator with bounded memory usage."""

    def __init__(self, hass: HomeAssistant):
        """Initialize."""
        super().__init__(...)
        self._history = deque(maxlen=1000)  # Max 1000 entries

    async def _async_update_data(self):
        """Fetch and store limited history."""
        data = await self.api.fetch()
        self._history.append(data)
        return data
```

### Clean Up Resources

```python
class ResourceManagingCoordinator(DataUpdateCoordinator):
    """Coordinator that cleans up properly."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession):
        """Initialize."""
        super().__init__(...)
        self._session = session

    async def _async_shutdown(self) -> None:
        """Clean up on shutdown."""
        await self._session.close()
        await super()._async_shutdown()
```

---

## Async Best Practices

### Use Async Libraries

```python
# ✅ CORRECT - Async HTTP client
import aiohttp

async def fetch_data(self):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# ❌ WRONG - Blocking HTTP client
import requests

async def fetch_data(self):
    # Blocks entire HA!
    return requests.get(url).json()
```

### Set Timeouts

```python
import aiohttp
from aiohttp import ClientTimeout

# ✅ GOOD - Explicit timeout
timeout = ClientTimeout(total=10)
async with aiohttp.ClientSession(timeout=timeout) as session:
    async with session.get(url) as response:
        return await response.json()


# ⚠️ BETTER - Different timeouts for different operations
timeout = ClientTimeout(
    total=30,      # Total request time
    connect=5,     # Connection establishment
    sock_read=10,  # Reading response
)
```

### Parallel Requests

```python
import asyncio

# ✅ GOOD - Parallel requests
async def fetch_all_devices(self):
    """Fetch data for all devices in parallel."""
    results = await asyncio.gather(
        self.api.fetch_device_1(),
        self.api.fetch_device_2(),
        self.api.fetch_device_3(),
        return_exceptions=True,  # Don't fail if one fails
    )
    return results


# ❌ WRONG - Sequential requests
async def fetch_all_devices_slow(self):
    """Fetch devices one by one (slow!)."""
    device_1 = await self.api.fetch_device_1()  # Wait
    device_2 = await self.api.fetch_device_2()  # Wait
    device_3 = await self.api.fetch_device_3()  # Wait
    return [device_1, device_2, device_3]
```

---

## Common Performance Anti-Patterns

### Anti-Pattern 1: Polling in Entities

```python
# ❌ WRONG
class BadEntity(SensorEntity):
    async def async_update(self):
        self._state = await fetch_data()  # Each entity polls!

# ✅ CORRECT
class GoodEntity(CoordinatorEntity):
    @property
    def native_value(self):
        return self.coordinator.data  # Shared data
```

### Anti-Pattern 2: Excessive Update Intervals

```python
# ❌ WRONG - Updates every second (overkill!)
update_interval=timedelta(seconds=1)

# ✅ CORRECT - Appropriate interval
update_interval=timedelta(seconds=30)
```

### Anti-Pattern 3: Not Using `always_update=False`

```python
# ❌ WRONG - Updates entities even when data unchanged
DataUpdateCoordinator(..., always_update=True)

# ✅ CORRECT - Only update entities when data changes
DataUpdateCoordinator(..., always_update=False)
```

### Anti-Pattern 4: Creating New Sessions Per Request

```python
# ❌ WRONG - Creates new session every request
async def fetch_data(self):
    async with aiohttp.ClientSession() as session:  # Expensive!
        async with session.get(url) as response:
            return await response.json()

# ✅ CORRECT - Reuse session
class API:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def fetch_data(self):
        async with self._session.get(url) as response:
            return await response.json()

    async def close(self):
        await self._session.close()
```

---

## Performance Checklist

Use this checklist to ensure optimal performance:

- [ ] Single coordinator per device/service (not per entity)
- [ ] Update interval appropriate for device type (30-60s for sensors)
- [ ] `always_update=False` if data doesn't always change
- [ ] Entities use CoordinatorEntity (not manual polling)
- [ ] Async libraries used for all I/O (aiohttp, not requests)
- [ ] Timeouts set on all network requests (5-30 seconds)
- [ ] Parallel requests used for multiple devices (asyncio.gather)
- [ ] Data structures are efficient (NamedTuple, dataclass)
- [ ] Memory usage bounded (deque with maxlen, not unlimited lists)
- [ ] Resources cleaned up on shutdown (sessions closed)
- [ ] No blocking code in async functions
- [ ] State changes minimized (round values, use should_poll=False)

---

## Profiling Performance

### Enable Debug Logging

```python
# In configuration.yaml
logger:
  default: info
  logs:
    custom_components.your_integration: debug
```

### Monitor Coordinator Updates

```python
import time

class ProfilingCoordinator(DataUpdateCoordinator):
    """Coordinator with built-in profiling."""

    async def _async_update_data(self):
        """Fetch data with timing."""
        start = time.time()

        try:
            data = await self.api.fetch_data()
            duration = time.time() - start

            _LOGGER.debug("Update completed in %.2fs", duration)

            if duration > 5.0:
                _LOGGER.warning("Update took %.2fs (slow!)", duration)

            return data
        except Exception as err:
            duration = time.time() - start
            _LOGGER.error("Update failed after %.2fs: %s", duration, err)
            raise
```

---

**Remember:** Performance optimization is about finding the right balance between responsiveness and resource usage. Measure first, optimize second!
