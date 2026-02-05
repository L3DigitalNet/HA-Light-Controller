"""Constants for the Example Device integration.

This module centralizes all constants used throughout the integration,
making it easy to maintain consistency and update values in one place.
"""

from datetime import timedelta
from typing import Final

# The domain is the unique identifier for your integration.
# It must match the folder name and the domain in manifest.json.
DOMAIN: Final = "example_device"

# Default polling interval - balance between freshness and resource usage.
# For local devices, 30 seconds is usually appropriate.
# For cloud APIs, consider rate limits (often 60+ seconds).
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=30)

# Configuration constants (these match the keys in config_flow)
CONF_DEVICE_ID: Final = "device_id"

# Platforms that this integration will set up.
# Add or remove based on what entity types your device supports.
PLATFORMS: Final = ["sensor", "binary_sensor", "switch"]

# Attribute keys - using constants prevents typos
ATTR_FIRMWARE_VERSION: Final = "firmware_version"
ATTR_LAST_SEEN: Final = "last_seen"
