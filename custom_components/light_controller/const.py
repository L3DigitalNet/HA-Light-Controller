"""Constants for the Light Controller integration."""

from typing import Final

# Integration domain
DOMAIN: Final = "light_controller"

# Service names
SERVICE_ENSURE_STATE: Final = "ensure_state"
SERVICE_ACTIVATE_PRESET: Final = "activate_preset"
SERVICE_CREATE_PRESET: Final = "create_preset"
SERVICE_DELETE_PRESET: Final = "delete_preset"
SERVICE_CREATE_PRESET_FROM_CURRENT: Final = "create_preset_from_current"

# Platforms
PLATFORMS: Final = ["button", "sensor"]

# Config entry keys (setup wizard)
CONF_NAME: Final = "name"

# Options keys (configurable defaults)
CONF_DEFAULT_BRIGHTNESS_PCT: Final = "default_brightness_pct"
CONF_DEFAULT_TRANSITION: Final = "default_transition"
CONF_BRIGHTNESS_TOLERANCE: Final = "brightness_tolerance"
CONF_RGB_TOLERANCE: Final = "rgb_tolerance"
CONF_KELVIN_TOLERANCE: Final = "kelvin_tolerance"
CONF_DELAY_AFTER_SEND: Final = "delay_after_send"
CONF_MAX_RETRIES: Final = "max_retries"
CONF_MAX_RUNTIME_SECONDS: Final = "max_runtime_seconds"
CONF_USE_EXPONENTIAL_BACKOFF: Final = "use_exponential_backoff"
CONF_MAX_BACKOFF_SECONDS: Final = "max_backoff_seconds"
CONF_NOTIFY_ON_FAILURE: Final = "notify_on_failure"
CONF_LOG_SUCCESS: Final = "log_success"

# Default values
DEFAULT_BRIGHTNESS_PCT: Final = 100
DEFAULT_TRANSITION: Final = 0.0
DEFAULT_BRIGHTNESS_TOLERANCE: Final = 3
DEFAULT_RGB_TOLERANCE: Final = 10
DEFAULT_KELVIN_TOLERANCE: Final = 150
DEFAULT_DELAY_AFTER_SEND: Final = 2.0
DEFAULT_MAX_RETRIES: Final = 3
DEFAULT_MAX_RUNTIME_SECONDS: Final = 60.0
DEFAULT_USE_EXPONENTIAL_BACKOFF: Final = False
DEFAULT_MAX_BACKOFF_SECONDS: Final = 30.0
DEFAULT_LOG_SUCCESS: Final = False

# Service parameter keys
ATTR_ENTITIES: Final = "entities"
ATTR_STATE_TARGET: Final = "state"
ATTR_DEFAULT_BRIGHTNESS_PCT: Final = "brightness_pct"
ATTR_DEFAULT_RGB_COLOR: Final = "rgb_color"
ATTR_DEFAULT_COLOR_TEMP_KELVIN: Final = "color_temp_kelvin"
ATTR_DEFAULT_EFFECT: Final = "effect"
ATTR_TARGETS: Final = "targets"
ATTR_BRIGHTNESS_TOLERANCE: Final = "brightness_tolerance"
ATTR_RGB_TOLERANCE: Final = "rgb_tolerance"
ATTR_KELVIN_TOLERANCE: Final = "kelvin_tolerance"
ATTR_TRANSITION: Final = "transition"
ATTR_DELAY_AFTER_SEND: Final = "delay_after_send"
ATTR_MAX_RETRIES: Final = "max_retries"
ATTR_MAX_RUNTIME_SECONDS: Final = "max_runtime_seconds"
ATTR_USE_EXPONENTIAL_BACKOFF: Final = "use_exponential_backoff"
ATTR_MAX_BACKOFF_SECONDS: Final = "max_backoff_seconds"
ATTR_SKIP_VERIFICATION: Final = "skip_verification"
ATTR_LOG_SUCCESS: Final = "log_success"
ATTR_NOTIFY_ON_FAILURE: Final = "notify_on_failure"

# Result keys
RESULT_SUCCESS: Final = "success"
RESULT_CODE: Final = "result"
RESULT_MESSAGE: Final = "message"
RESULT_ATTEMPTS: Final = "attempts"
RESULT_TOTAL_LIGHTS: Final = "total_lights"
RESULT_FAILED_LIGHTS: Final = "failed_lights"
RESULT_SKIPPED_LIGHTS: Final = "skipped_lights"
RESULT_ELAPSED_SECONDS: Final = "elapsed_seconds"

# Result codes
RESULT_CODE_SUCCESS: Final = "success"
RESULT_CODE_FAILED: Final = "failed"
RESULT_CODE_TIMEOUT: Final = "timeout"
RESULT_CODE_ERROR: Final = "error"
RESULT_CODE_NO_VALID_ENTITIES: Final = "no_valid_entities"

# Supported color modes
COLOR_MODE_RGB: Final = "rgb"
COLOR_MODE_HS: Final = "hs"
COLOR_MODE_COLOR_TEMP: Final = "color_temp"

# Preset storage keys
CONF_PRESETS: Final = "presets"
PRESET_ID: Final = "id"
PRESET_NAME: Final = "name"
PRESET_ENTITIES: Final = "entities"
PRESET_STATE: Final = "state"
PRESET_BRIGHTNESS_PCT: Final = "brightness_pct"
PRESET_RGB_COLOR: Final = "rgb_color"
PRESET_COLOR_TEMP_KELVIN: Final = "color_temp_kelvin"
PRESET_EFFECT: Final = "effect"
PRESET_TARGETS: Final = "targets"
PRESET_TRANSITION: Final = "transition"
PRESET_SKIP_VERIFICATION: Final = "skip_verification"

# Preset service attributes
ATTR_PRESET: Final = "preset"
ATTR_PRESET_NAME: Final = "name"
ATTR_PRESET_ID: Final = "preset_id"

# Preset status
PRESET_STATUS_IDLE: Final = "idle"
PRESET_STATUS_ACTIVATING: Final = "activating"
PRESET_STATUS_SUCCESS: Final = "success"
PRESET_STATUS_FAILED: Final = "failed"

# Entity IDs
BUTTON_ENTITY_PREFIX: Final = "button"
SENSOR_ENTITY_PREFIX: Final = "sensor"
