---
name: ha-debugging
description: Debug and troubleshoot Home Assistant integration issues. Use when the user mentions "error", "debug", "not working", "unavailable", "traceback", "exception", "logs", "failing", or needs help diagnosing problems with a Home Assistant integration. Also triggers on "ConfigEntryNotReady", "UpdateFailed", "entity not found", or stack traces from Home Assistant.
---

# Debugging Home Assistant Integrations

## Diagnostic Checklist

When diagnosing an integration issue, work through these steps systematically.

### Step 1: Enable Debug Logging

Add to `configuration.yaml` and restart:

```yaml
logger:
  default: warning
  logs:
    custom_components.{domain}: debug
    homeassistant.config_entries: debug
```

View logs at Settings → System → Logs, or via CLI: `tail -f config/home-assistant.log`

### Step 2: Identify the Error Category

| Symptom | Likely Cause | Where to Look |
|---|---|---|
| Integration won't load | Import error or manifest issue | `__init__.py`, `manifest.json` |
| "Config flow could not be loaded" | Syntax error in config_flow.py | `config_flow.py`, `strings.json` |
| "Unexpected exception" in setup | Unhandled error in config flow | Config flow validation logic |
| Entities show "unavailable" | Coordinator UpdateFailed | `coordinator.py` |
| Entities don't appear | Missing platform forward or `async_add_entities` | `__init__.py`, platform files |
| "ConfigEntryNotReady" | First refresh failed | Coordinator or API connection |
| State not updating | Coordinator subscription broken | Entity `__init__` missing `super().__init__()` |

### Step 3: Common Fixes by Error Type

**ImportError / ModuleNotFoundError:**
```python
# Check 1: Are relative imports correct?
from .const import DOMAIN  # RIGHT
from custom_components.my_integration.const import DOMAIN  # WRONG in package context

# Check 2: Is manifest.json requirements correct?
# "requirements": ["my-library==1.0.0"]

# Check 3: Does __init__.py exist in the integration folder?
```

**Config flow "Unexpected exception":**
```python
# Check: Is errors dict initialized?
async def async_step_user(self, user_input=None):
    errors: dict[str, str] = {}  # Must exist!

# Check: Are all strings.json keys present for every error?
# Every errors["base"] = "key" must have a matching entry in strings.json

# Check: Does the domain match everywhere?
# manifest.json domain == const.py DOMAIN == config_flow.py ConfigFlow(domain=DOMAIN)
```

**Entities unavailable:**
```python
# Check 1: Is _async_update_data raising UpdateFailed?
async def _async_update_data(self):
    try:
        return await self.client.get_data()
    except Exception as err:
        raise UpdateFailed(f"Error: {err}") from err  # This marks entities unavailable

# Check 2: Is the entity's available property too restrictive?
@property
def available(self) -> bool:
    return super().available and self._device_id in self.coordinator.data

# Check 3: Did async_config_entry_first_refresh() succeed?
# If it fails, ConfigEntryNotReady is raised and setup retries
```

**Entities not appearing:**
```python
# Check 1: Is the platform in the PLATFORMS list?
PLATFORMS = [Platform.SENSOR, Platform.SWITCH]  # Must include your platform

# Check 2: Is async_forward_entry_setups called?
await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

# Check 3: Does async_setup_entry call async_add_entities?
async def async_setup_entry(hass, entry, async_add_entities):
    entities = [MySensor(coordinator, "temp")]
    async_add_entities(entities)  # Must be called!

# Check 4: Is the entity list empty due to data filtering?
# If you filter entities based on data, check that data contains expected keys
```

**Blocking event loop (HA logs "Detected blocking call"):**
```python
# Find the sync call and wrap it:
# WRONG
data = requests.get(url)

# RIGHT
data = await hass.async_add_executor_job(requests.get, url)
```

**State not updating after coordinator refresh:**
```python
# Check: Does entity inherit CoordinatorEntity FIRST?
class MySensor(CoordinatorEntity[MyCoordinator], SensorEntity):  # Correct order!

# Check: Is super().__init__(coordinator) called?
def __init__(self, coordinator):
    super().__init__(coordinator)  # Required!

# Check: Does native_value read from self.coordinator.data?
@property
def native_value(self):
    return self.coordinator.data.get("value")  # Must use coordinator.data
```

## Useful Diagnostic Commands

```bash
# Validate JSON files
python -c "import json; json.load(open('manifest.json')); print('OK')"
python -c "import json; json.load(open('strings.json')); print('OK')"

# Check Python syntax
python -m py_compile __init__.py
python -m py_compile config_flow.py

# Run linter
ruff check .

# Type check
mypy .

# View config entries storage
cat config/.storage/core.config_entries | python -m json.tool | grep -A 20 '{domain}'

# Check if integration loaded
grep '{domain}' config/home-assistant.log | tail -20
```

## Debugging Workflow

1. **Reproduce** — Identify the exact steps that cause the problem
2. **Enable debug logging** — Set the integration to debug level
3. **Check logs** — Look for the first error in the chain, not the last
4. **Isolate** — Determine which file and function contains the error
5. **Fix** — Apply the targeted fix from the patterns above
6. **Verify** — Restart HA and confirm the fix resolves the issue
7. **Test** — Write a test that would catch this regression
