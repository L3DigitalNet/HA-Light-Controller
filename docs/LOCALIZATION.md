# Localization Guide

This guide explains how to add multi-language support to your Home Assistant integration, making it accessible to users worldwide.

## Table of Contents

- [Overview](#overview)
- [File Structure](#file-structure)
- [strings.json](#stringsjson)
- [Translation Files](#translation-files)
- [Dynamic Strings](#dynamic-strings)
- [Best Practices](#best-practices)
- [Testing Translations](#testing-translations)

---

## Overview

Home Assistant uses a translation system that separates user-visible strings from code logic. All text shown in the UI should be translatable.

### What Gets Translated?

- Config flow steps and forms
- Error messages
- Entity names and descriptions
- Service descriptions
- Device information
- Options flow text

### What Doesn't Need Translation?

- Entity unique_ids
- Domain names
- Internal constants
- Log messages (always in English)
- API endpoints

---

## File Structure

```
custom_components/your_integration/
├── strings.json                    # English translations (required)
├── translations/
│   ├── en.json                     # English (copy of strings.json)
│   ├── de.json                     # German
│   ├── es.json                     # Spanish
│   ├── fr.json                     # French
│   ├── it.json                     # Italian
│   ├── nl.json                     # Dutch
│   ├── pl.json                     # Polish
│   ├── pt.json                     # Portuguese
│   ├── ru.json                     # Russian
│   ├── sv.json                     # Swedish
│   └── zh-Hans.json                # Chinese (Simplified)
```

**Important:** `strings.json` is the source of truth. Translation files are copies with translated values.

---

## strings.json

### Basic Structure

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Set up Your Integration",
        "description": "Enter your device connection details.",
        "data": {
          "host": "Host",
          "port": "Port",
          "api_key": "API Key"
        },
        "data_description": {
          "host": "IP address or hostname of the device",
          "api_key": "API key from device settings"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to the device. Check the host and port.",
      "invalid_auth": "Invalid API key. Please check your credentials.",
      "unknown": "An unexpected error occurred. Please try again."
    },
    "abort": {
      "already_configured": "This device is already configured.",
      "reauth_successful": "Re-authentication was successful."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Configure Options",
        "data": {
          "update_interval": "Update interval (seconds)",
          "enable_sensors": "Enable additional sensors"
        }
      }
    }
  }
}
```

### Config Flow Sections

#### step Section

Defines each step in the config flow:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Initial Setup",
        "description": "Provide connection information",
        "data": {
          "host": "Hostname",
          "username": "Username",
          "password": "Password"
        }
      },
      "discovery": {
        "title": "Confirm Discovered Device",
        "description": "We found a device at {host}. Confirm to add it."
      },
      "oauth": {
        "title": "Authorize Access",
        "description": "Click the link below to authorize Home Assistant."
      }
    }
  }
}
```

#### error Section

Defines error messages:

```json
{
  "config": {
    "error": {
      "cannot_connect": "Unable to connect. Check network settings.",
      "invalid_auth": "Authentication failed. Verify credentials.",
      "timeout": "Connection timed out. Try again.",
      "unknown": "Unexpected error occurred."
    }
  }
}
```

#### abort Section

Defines abort/completion messages:

```json
{
  "config": {
    "abort": {
      "already_configured": "Device already configured",
      "no_devices_found": "No devices found on network",
      "reauth_successful": "Re-authentication successful"
    }
  }
}
```

### Options Flow

```json
{
  "options": {
    "step": {
      "init": {
        "title": "Integration Options",
        "description": "Configure integration behavior",
        "data": {
          "scan_interval": "Update frequency (seconds)",
          "timeout": "Connection timeout (seconds)"
        },
        "data_description": {
          "scan_interval": "How often to poll for updates (minimum 10 seconds)",
          "timeout": "Maximum time to wait for responses"
        }
      }
    }
  }
}
```

---

## Translation Files

### Creating Translation Files

Translation files in `translations/` are JSON files with the same structure as `strings.json` but with translated values.

**Example: translations/de.json (German)**

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Ihre Integration einrichten",
        "description": "Geben Sie die Verbindungsdetails Ihres Geräts ein.",
        "data": {
          "host": "Host",
          "port": "Port",
          "api_key": "API-Schlüssel"
        },
        "data_description": {
          "host": "IP-Adresse oder Hostname des Geräts",
          "api_key": "API-Schlüssel aus den Geräteeinstellungen"
        }
      }
    },
    "error": {
      "cannot_connect": "Verbindung zum Gerät fehlgeschlagen. Überprüfen Sie Host und Port.",
      "invalid_auth": "Ungültiger API-Schlüssel. Bitte überprüfen Sie Ihre Anmeldedaten.",
      "unknown": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut."
    },
    "abort": {
      "already_configured": "Dieses Gerät ist bereits konfiguriert.",
      "reauth_successful": "Erneute Authentifizierung war erfolgreich."
    }
  }
}
```

### Partial Translations

You don't need to translate everything at once:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Configuration de l'intégration",
        "data": {
          "host": "Hôte",
          "api_key": "Clé API"
        }
      }
    },
    "error": {
      "cannot_connect": "Impossible de se connecter à l'appareil.",
      "invalid_auth": "Clé API invalide."
    }
  }
}
```

**Note:** Untranslated strings fall back to English from `strings.json`.

---

## Dynamic Strings

### Placeholders

Use placeholders for dynamic content:

```json
{
  "config": {
    "step": {
      "discovery": {
        "description": "Found device: {name} at {host}"
      }
    },
    "error": {
      "version_mismatch": "Device version {version} is not supported. Minimum version: {min_version}"
    }
  }
}
```

In Python code:

```python
from homeassistant.data_entry_flow import FlowResult

async def async_step_discovery(self, discovery_info):
    """Handle discovery."""
    return self.async_show_form(
        step_id="discovery",
        description_placeholders={
            "name": discovery_info["name"],
            "host": discovery_info["host"],
        },
    )

# Error with placeholders
errors = {}
if version_mismatch:
    errors["base"] = "version_mismatch"
    self._errors_placeholders = {
        "version": device_version,
        "min_version": MINIMUM_VERSION,
    }
```

### Pluralization

Home Assistant doesn't have built-in pluralization. Use separate strings:

```json
{
  "config": {
    "step": {
      "select_device": {
        "description_one": "Found 1 device",
        "description_other": "Found {count} devices"
      }
    }
  }
}
```

In code:

```python
device_count = len(devices)
key = "description_one" if device_count == 1 else "description_other"
description = self.hass.localize(f"component.{DOMAIN}.config.step.select_device.{key}")

# With placeholder
if device_count > 1:
    description = description.format(count=device_count)
```

---

## Best Practices

### 1. Keep Keys Descriptive

```json
// ✅ GOOD - Clear, descriptive keys
{
  "error": {
    "device_offline": "Device is offline",
    "invalid_api_key": "Invalid API key",
    "rate_limit_exceeded": "Too many requests"
  }
}

// ❌ BAD - Generic keys
{
  "error": {
    "error1": "Device is offline",
    "error2": "Invalid API key",
    "error3": "Too many requests"
  }
}
```

### 2. Provide Context in Descriptions

```json
{
  "config": {
    "step": {
      "user": {
        "data_description": {
          "host": "IP address or hostname (e.g., 192.168.1.100)",
          "port": "TCP port number (default: 8080)",
          "timeout": "Connection timeout in seconds (5-60)"
        }
      }
    }
  }
}
```

### 3. Write User-Friendly Error Messages

```json
{
  "error": {
    // ✅ GOOD - Actionable, specific
    "cannot_connect": "Unable to connect to {host}. Please check that the device is powered on and connected to the network.",

    // ❌ BAD - Vague, technical
    "cannot_connect": "ConnectionError: timeout"
  }
}
```

### 4. Use Consistent Terminology

```json
{
  "config": {
    "step": {
      "user": {
        "data": {
          "api_key": "API Key"  // Always "API Key"
        }
      }
    },
    "error": {
      "invalid_auth": "Invalid API Key"  // Not "Invalid Key" or "Bad Token"
    }
  }
}
```

### 5. Avoid Technical Jargon

```json
{
  // ✅ GOOD - User-friendly
  "error": {
    "device_not_found": "Could not find the device on your network"
  },

  // ❌ BAD - Technical
  "error": {
    "device_not_found": "EHOSTUNREACH: No route to host"
  }
}
```

---

## Testing Translations

### Test with Different Languages

1. **Change HA language:**
   - Go to User Profile
   - Change language to test translation

2. **Verify placeholders work:**
   ```python
   # Trigger error with placeholder
   errors["base"] = "device_offline"
   description_placeholders = {"device_name": "Living Room Sensor"}
   ```

3. **Check fallbacks:**
   - Remove translation file
   - Verify English strings appear

### Validate JSON Structure

```bash
# Validate JSON syntax
python -m json.tool custom_components/your_integration/strings.json

# Validate translation file
python -m json.tool custom_components/your_integration/translations/de.json
```

### Common Issues

**Issue: Strings not translating**
- Check language code matches (e.g., `de` not `german`)
- Verify JSON structure matches `strings.json`
- Restart Home Assistant after changes

**Issue: Placeholder not replaced**
- Ensure placeholder name matches exactly
- Check `description_placeholders` is passed correctly
- Verify placeholder syntax: `{placeholder_name}`

**Issue: Missing translation**
- Check translation file exists in `translations/`
- Verify key path matches `strings.json`
- Falls back to English if translation missing

---

## Contributing Translations

### For Integration Authors

1. **Create strings.json** with all UI text
2. **Add translations/** directory
3. **Copy to en.json**: `cp strings.json translations/en.json`
4. **Document translation need** in CONTRIBUTING.md

### For Translators

1. **Copy strings.json** to `translations/{language_code}.json`
2. **Translate values** (not keys!)
3. **Keep JSON structure** identical
4. **Submit pull request**

### Language Codes

Common language codes:
- `de` - German (Deutsch)
- `es` - Spanish (Español)
- `fr` - French (Français)
- `it` - Italian (Italiano)
- `nl` - Dutch (Nederlands)
- `pl` - Polish (Polski)
- `pt` - Portuguese (Português)
- `ru` - Russian (Русский)
- `sv` - Swedish (Svenska)
- `zh-Hans` - Chinese Simplified (简体中文)
- `zh-Hant` - Chinese Traditional (繁體中文)

Full list: https://github.com/home-assistant/core/tree/dev/homeassistant/components/frontend/translations

---

## Example: Complete strings.json

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Configure Your Integration",
        "description": "Enter the connection details for your device.",
        "data": {
          "host": "Host",
          "port": "Port",
          "username": "Username",
          "password": "Password",
          "verify_ssl": "Verify SSL Certificate"
        },
        "data_description": {
          "host": "IP address or hostname of the device (e.g., 192.168.1.100)",
          "port": "Port number (default: 8080)",
          "verify_ssl": "Enable SSL certificate verification (recommended)"
        }
      },
      "discovery": {
        "title": "Discovered Device",
        "description": "We found a {model} at {host}. Do you want to set it up?"
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to {host}. Please verify the device is online and accessible.",
      "invalid_auth": "Authentication failed. Please check your username and password.",
      "invalid_host": "Invalid hostname or IP address format.",
      "timeout": "Connection timed out after {timeout} seconds. The device may be offline.",
      "ssl_error": "SSL certificate verification failed. You can disable verification in settings (not recommended).",
      "unknown": "An unexpected error occurred: {error}"
    },
    "abort": {
      "already_configured": "This device is already configured in Home Assistant.",
      "no_devices_found": "No devices were found on your network. Please check that devices are powered on.",
      "reauth_successful": "Re-authentication was successful. Your integration is working again."
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Integration Options",
        "description": "Configure how the integration behaves.",
        "data": {
          "scan_interval": "Update Interval (seconds)",
          "timeout": "Connection Timeout (seconds)",
          "enable_debug": "Enable Debug Logging"
        },
        "data_description": {
          "scan_interval": "How often to poll the device for updates (minimum: 10 seconds)",
          "timeout": "Maximum time to wait for device responses (5-60 seconds)",
          "enable_debug": "Write detailed diagnostic information to logs"
        }
      }
    }
  }
}
```

---

## Resources

- **HA Translations**: https://developers.home-assistant.io/docs/internationalization/
- **Translation Guidelines**: https://developers.home-assistant.io/docs/internationalization/translation_guidelines/
- **Lokalise (HA's translation platform)**: https://lokalise.com/

---

**Remember:** Good translations make your integration accessible to millions of non-English speakers worldwide. Invest time in clear, user-friendly strings!
