# Config Entry Migration Guide

This guide explains how to handle config entry migrations when you need to change the structure of stored configuration data in your Home Assistant integration.

## Table of Contents

- [When to Migrate](#when-to-migrate)
- [Version Management](#version-management)
- [Implementing Migrations](#implementing-migrations)
- [Common Migration Scenarios](#common-migration-scenarios)
- [Testing Migrations](#testing-migrations)
- [Best Practices](#best-practices)

---

## When to Migrate

You need to implement a config entry migration when:

### 1. Changing Data Structure

```python
# Version 1 - Simple string
data = {"host": "192.168.1.100"}

# Version 2 - Need structured connection info
data = {
    "connection": {
        "host": "192.168.1.100",
        "port": 8080,
        "protocol": "https",
    }
}
```

### 2. Renaming Fields

```python
# Version 1
data = {"api_key": "abc123"}

# Version 2 - More descriptive name
data = {"access_token": "abc123"}
```

### 3. Adding Required Fields

```python
# Version 1
data = {"host": "192.168.1.100"}

# Version 2 - New required field
data = {
    "host": "192.168.1.100",
    "device_type": "sensor",  # New required field
}
```

### 4. Changing Data Types

```python
# Version 1 - Port as string
data = {"port": "8080"}

# Version 2 - Port as integer
data = {"port": 8080}
```

### When NOT to Migrate

- Adding optional fields with defaults (just use `.get()`)
- Removing unused fields (old data is harmless)
- Changing internal code structure (doesn't affect stored data)

---

## Version Management

### Current Version in manifest.json

The integration version in `manifest.json` is **separate** from config entry version:

```json
{
  "domain": "your_integration",
  "version": "1.2.3",  ← Integration version (for HACS, releases)
  "..."
}
```

### Config Entry Version

Config entry version tracks data structure changes:

```python
# In config_flow.py
class YourConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 2  ← Config entry version (for migrations)
```

**Important:** Only increment `VERSION` when the data structure changes, not for every integration release.

---

## Implementing Migrations

### Basic Migration Pattern

Add `async_migrate_entry()` to your `__init__.py`:

```python
"""Your Integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        # Migrate version 1 → 2
        new_data = {**config_entry.data}

        # Perform migration
        new_data["new_field"] = "default_value"

        # Update entry
        config_entry.version = 2
        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
        )

    if config_entry.version == 2:
        # Migrate version 2 → 3 (if needed)
        new_data = {**config_entry.data}

        # Transform data structure
        new_data["transformed_field"] = transform(new_data["old_field"])
        del new_data["old_field"]

        config_entry.version = 3
        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
        )

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True
```

### Migration Flow

```
User starts HA
    ↓
HA loads config entries
    ↓
Config entry version < ConfigFlow.VERSION?
    ↓ Yes
async_migrate_entry() called
    ↓
Migration successful?
    ↓ Yes
async_setup_entry() called
    ↓
Integration loads normally
```

---

## Common Migration Scenarios

### Scenario 1: Adding a New Required Field

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        new_data = {**config_entry.data}

        # Add new required field with sensible default
        new_data["update_interval"] = 30

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

        _LOGGER.info(
            "Added 'update_interval' field with default value 30. "
            "You can change this in integration options."
        )

    return True
```

### Scenario 2: Renaming a Field

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        new_data = {**config_entry.data}

        # Rename field
        if "api_key" in new_data:
            new_data["access_token"] = new_data.pop("api_key")

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

    return True
```

### Scenario 3: Restructuring Nested Data

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        old_data = config_entry.data

        # Transform flat structure to nested
        new_data = {
            "connection": {
                "host": old_data["host"],
                "port": old_data.get("port", 8080),
                "protocol": old_data.get("protocol", "http"),
            },
            "authentication": {
                "username": old_data["username"],
                "password": old_data["password"],
            },
        }

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

    return True
```

### Scenario 4: Changing Data Types

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        new_data = {**config_entry.data}

        # Convert string port to integer
        if "port" in new_data and isinstance(new_data["port"], str):
            try:
                new_data["port"] = int(new_data["port"])
            except ValueError:
                _LOGGER.warning("Invalid port value, using default 8080")
                new_data["port"] = 8080

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

    return True
```

### Scenario 5: Migrating Options

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        # Migrate both data and options
        new_data = {**config_entry.data}
        new_options = {**config_entry.options}

        # Move field from data to options
        if "update_interval" in new_data:
            new_options["update_interval"] = new_data.pop("update_interval")

        config_entry.version = 2
        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
            options=new_options,
        )

    return True
```

---

## Testing Migrations

### Unit Test Example

```python
"""Test config entry migrations."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

from custom_components.your_integration import async_migrate_entry


async def test_migrate_v1_to_v2(hass):
    """Test migration from version 1 to 2."""
    # Create v1 config entry
    entry = ConfigEntry(
        version=1,
        domain="your_integration",
        title="Test Device",
        data={
            CONF_HOST: "192.168.1.100",
            "api_key": "abc123",  # Old field name
        },
        source="user",
    )

    # Run migration
    assert await async_migrate_entry(hass, entry)

    # Verify migration
    assert entry.version == 2
    assert "access_token" in entry.data  # New field name
    assert "api_key" not in entry.data  # Old field removed
    assert entry.data["access_token"] == "abc123"


async def test_migrate_with_missing_field(hass):
    """Test migration handles missing fields gracefully."""
    entry = ConfigEntry(
        version=1,
        domain="your_integration",
        title="Test Device",
        data={CONF_HOST: "192.168.1.100"},  # Missing api_key
        source="user",
    )

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    # Verify default was added
    assert "update_interval" in entry.data
```

### Manual Testing

1. **Install old version** of your integration
2. **Configure** it and ensure it works
3. **Note the data structure** (check `.storage/core.config_entries`)
4. **Update to new version** with migration
5. **Restart Home Assistant**
6. **Verify** integration still works
7. **Check logs** for migration messages

---

## Best Practices

### 1. Log Migration Actions

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.info(
        "Migrating %s from version %s to version %s",
        config_entry.title,
        config_entry.version,
        VERSION,
    )

    # ... migration code ...

    _LOGGER.info("Migration successful")
    return True
```

### 2. Handle Missing Fields Gracefully

```python
# ✅ GOOD - Use .get() with defaults
new_data["port"] = config_entry.data.get("port", 8080)

# ❌ BAD - Can cause KeyError
new_data["port"] = config_entry.data["port"]
```

### 3. Preserve User Data

```python
# ✅ GOOD - Keep all existing data
new_data = {**config_entry.data}  # Copy all fields
new_data["new_field"] = "default"  # Add new field

# ❌ BAD - Loses existing data
new_data = {"new_field": "default"}  # Old data lost!
```

### 4. Validate Migrated Data

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        new_data = {**config_entry.data}

        # Add new field
        new_data["timeout"] = 30

        # Validate
        if not isinstance(new_data["timeout"], int):
            _LOGGER.error("Migration validation failed: invalid timeout type")
            return False

        if not 1 <= new_data["timeout"] <= 300:
            _LOGGER.error("Migration validation failed: timeout out of range")
            return False

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

    return True
```

### 5. Provide User Notifications

```python
from homeassistant.helpers import issue_registry as ir

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        # ... migration ...

        # Notify user of changes
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"migration_{config_entry.entry_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.INFO,
            translation_key="migration_success",
            translation_placeholders={
                "version": str(config_entry.version),
                "changes": "Added update_interval setting (default: 30s)",
            },
        )

    return True
```

### 6. Support Multi-Step Migrations

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry through multiple versions."""
    # Migrate 1 → 2 → 3 → 4 step by step

    if config_entry.version < 2:
        # Migrate 1 → 2
        _migrate_v1_to_v2(config_entry)

    if config_entry.version < 3:
        # Migrate 2 → 3
        _migrate_v2_to_v3(config_entry)

    if config_entry.version < 4:
        # Migrate 3 → 4
        _migrate_v3_to_v4(config_entry)

    return True


def _migrate_v1_to_v2(config_entry: ConfigEntry) -> None:
    """Migrate version 1 to 2."""
    new_data = {**config_entry.data}
    new_data["new_field_v2"] = "default"
    config_entry.version = 2
    hass.config_entries.async_update_entry(config_entry, data=new_data)
```

---

## Troubleshooting

### Migration Fails

If `async_migrate_entry()` returns `False`:
- Integration won't load
- User must delete and re-add integration
- **Avoid this!** Always return `True` even if migration isn't perfect

```python
async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    try:
        # ... migration code ...
        return True
    except Exception as err:
        _LOGGER.exception("Migration failed: %s", err)
        # Still return True to allow integration to load
        # Better to have partial migration than broken integration
        return True
```

### Data Loss

If migration loses user data:
- Check you're using `{**config_entry.data}` to copy
- Verify you're not overwriting with empty dict
- Test migration with real user data

### Infinite Migration Loop

If HA keeps running migration:
- Ensure you're updating `config_entry.version`
- Verify version matches `ConfigFlow.VERSION`
- Check you're calling `async_update_entry()`

---

## Resources

- **HA Developer Docs**: https://developers.home-assistant.io/docs/config_entries_config_flow_handler#migrating-config-entries
- **ConfigEntry API**: https://developers.home-assistant.io/docs/config_entries_index/
- **Example Migrations**: Search HA core for `async_migrate_entry` examples

---

**Remember:** Migrations run once per user per version. Test thoroughly before releasing!
