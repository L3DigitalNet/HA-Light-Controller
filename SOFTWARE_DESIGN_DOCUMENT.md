# Software Design Document: HA-Light-Controller

**Version:** 0.3.0 **Date:** February 18, 2026 **Status:** Current Implementation

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Architecture](#3-architecture)
4. [Component Design](#4-component-design)
5. [Data Design](#5-data-design)
6. [Interface Design](#6-interface-design)
7. [Behavioral Design](#7-behavioral-design)
8. [Configuration and Deployment](#8-configuration-and-deployment)
9. [Quality Attributes](#9-quality-attributes)
10. [Constraints and Assumptions](#10-constraints-and-assumptions)

---

## 1. Introduction

### 1.1 Purpose

This document describes the software design of HA-Light-Controller, a Home Assistant
custom integration that provides reliable light control with state verification,
automatic retries, and preset management.

### 1.2 Scope

HA-Light-Controller addresses a real-world reliability problem: when Home Assistant
sends a `light.turn_on` command, it sends the command once and assumes success. In
environments with Zigbee/Z-Wave mesh networks, commands can be lost due to network
congestion, device unresponsiveness, or protocol-level issues. This integration adds a
verification-and-retry loop around light commands, ensuring lights actually reach their
target state.

The integration scope is intentionally narrow:

- Light state verification and retry logic
- Preset management for saved lighting configurations
- Service-based API for automation integration
- Entity platforms (buttons and sensors) for preset interaction

Notification features and blueprints were removed in v0.2.0 to maintain focus.

### 1.3 Definitions

| Term                | Definition                                                                                    |
| ------------------- | --------------------------------------------------------------------------------------------- |
| **Entity**          | A Home Assistant object representing a device or service (e.g., `light.living_room`)          |
| **Service**         | An action that can be called within Home Assistant (e.g., `light.turn_on`)                    |
| **ConfigEntry**     | A Home Assistant configuration entry created through the UI config flow                       |
| **Preset**          | A saved lighting configuration that can be activated by name or button press                  |
| **Verification**    | The process of checking whether a light's actual state matches the target state               |
| **Fire-and-forget** | A mode where commands are sent without subsequent verification                                |
| **Tolerance**       | The allowed deviation between actual and target values for brightness, color, and temperature |

### 1.4 System Context

```
┌─────────────────────────────────────────────────────────┐
│                   Home Assistant Core                    │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Event    │  │    State     │  │     Service      │  │
│  │   Bus     │  │   Machine    │  │    Registry      │  │
│  └──────────┘  └──────────────┘  └──────────────────┘  │
│        │              │                   │             │
│        └──────────────┼───────────────────┘             │
│                       │                                 │
│              ┌────────┴────────┐                        │
│              │  HA-Light-      │                        │
│              │  Controller     │                        │
│              └────────┬────────┘                        │
│                       │                                 │
│       ┌───────────────┼───────────────┐                 │
│       │               │               │                 │
│  ┌────┴────┐   ┌──────┴──────┐  ┌────┴──────┐          │
│  │ Zigbee  │   │  Z-Wave     │  │   WiFi    │          │
│  │ Lights  │   │  Lights     │  │  Lights   │          │
│  └─────────┘   └─────────────┘  └───────────┘          │
└─────────────────────────────────────────────────────────┘
```

The integration sits between Home Assistant's service layer and the underlying light
entities. It does not communicate with devices directly — it uses HA's
`light.turn_on`/`light.turn_off` services and reads state from HA's state machine.

---

## 2. System Overview

### 2.1 Design Goals

1. **Reliability over speed** — Verify lights reach target state; retry if they don't.
2. **Non-invasive** — Works with any light entity in HA without requiring
   device-specific code.
3. **Configurable** — Every parameter has a sensible default but can be overridden
   per-call or globally.
4. **Async-first** — All operations are non-blocking, compatible with HA's
   single-threaded event loop.
5. **Preset management** — Store and recall lighting scenes with per-entity granularity.

### 2.2 Key Design Decisions

| Decision                                | Rationale                                                                                                                                                                 |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **State verification via polling**      | HA's state machine is the source of truth. Polling after a delay is simpler and more reliable than event-based approaches, which can miss updates or arrive out of order. |
| **Exponential backoff**                 | Devices that fail to respond likely need more time, not more commands. Backoff prevents command flooding.                                                                 |
| **Group expansion at call time**        | Light groups are expanded to individual entities each time, ensuring membership changes are always reflected.                                                             |
| **Preset storage in ConfigEntry.data**  | Uses HA's built-in persistence mechanism. No external files, no database, survives restarts and migrations.                                                               |
| **Service registration in async_setup** | Services are registered once globally (not per-entry), so they survive config entry reloads. Handlers look up the active entry at call time.                              |
| **Per-entity target overrides**         | Allows a single service call to set different brightness/color for each light, avoiding N separate calls.                                                                 |
| **Runtime data on ConfigEntry**         | Uses HA 2025.2+ `runtime_data` pattern instead of `hass.data[DOMAIN]` dict, providing type safety and automatic cleanup.                                                  |
| **Listener pattern for entities**       | Preset button/sensor entities register as listeners on PresetManager, receiving updates through a callback pattern rather than polling.                                   |

---

## 3. Architecture

### 3.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        HA-Light-Controller                       │
│                                                                  │
│  ┌──────────┐    ┌────────────────┐    ┌─────────────────────┐  │
│  │ Config   │    │    __init__    │    │    Services         │  │
│  │  Flow    │    │  (Entry Point) │    │ (ensure_state,      │  │
│  │          │    │                │    │  activate_preset,   │  │
│  │ - user   │    │ - async_setup  │    │  create_preset,     │  │
│  │ - options│    │ - setup_entry  │    │  delete_preset,     │  │
│  │ - preset │    │ - unload_entry │    │  create_from_       │  │
│  │   CRUD   │    │                │    │  current)           │  │
│  └──────────┘    └───────┬────────┘    └──────────┬──────────┘  │
│                          │                        │              │
│                 ┌────────┴────────────────────────┘              │
│                 │                                                │
│        ┌───────┴────────┐      ┌──────────────────┐             │
│        │ LightController│      │  PresetManager   │             │
│        │                │◄─────│                  │             │
│        │ - ensure_state │      │ - CRUD presets   │             │
│        │ - expand       │      │ - activate       │             │
│        │ - verify       │      │ - status track   │             │
│        │ - retry        │      │ - listener mgmt  │             │
│        └───────┬────────┘      └────────┬─────────┘             │
│                │                        │                        │
│        ┌───────┴──────────────┬─────────┴────────┐              │
│        │                     │                   │              │
│   ┌────┴─────┐         ┌────┴─────┐       ┌────┴─────┐        │
│   │  Button  │         │  Sensor  │       │  Config  │        │
│   │ Platform │         │ Platform │       │  Entry   │        │
│   │          │         │          │       │  Storage │        │
│   │ (activate│         │ (status  │       │          │        │
│   │  preset) │         │  display)│       │ (presets │        │
│   └──────────┘         └──────────┘       │  + opts) │        │
│                                           └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Inventory

| Component       | File                | Lines | Responsibility                                                 |
| --------------- | ------------------- | ----- | -------------------------------------------------------------- |
| Entry Point     | `__init__.py`       | 692   | Service registration, parameter merging, lifecycle management  |
| Controller      | `controller.py`     | 909   | Core light control: expand, target, group, send, verify, retry |
| Preset Manager  | `preset_manager.py` | 418   | Preset storage, status tracking, activation delegation         |
| Config Flow     | `config_flow.py`    | 1026  | UI-based setup and options: settings, preset creation/editing  |
| Constants       | `const.py`          | 118   | All `CONF_*`, `ATTR_*`, `DEFAULT_*`, `PRESET_*` constants      |
| Button Platform | `button.py`         | 200   | Preset activation button entities                              |
| Sensor Platform | `sensor.py`         | 196   | Preset status sensor entities                                  |

### 3.3 Dependency Graph

```
const.py ◄─── controller.py
    ▲               ▲
    │               │
    ├──── __init__.py ────► preset_manager.py
    │                              ▲
    │                              │
    ├──── config_flow.py           │
    │                              │
    ├──── button.py ───────────────┤
    │                              │
    └──── sensor.py ───────────────┘
```

`const.py` is the dependency root, imported by every other module. `controller.py` has
no intra-package dependencies beyond `const.py`. `preset_manager.py` depends on
`controller.py` only via TYPE_CHECKING (for the `LightController` type hint), keeping
the runtime dependency minimal.

---

## 4. Component Design

### 4.1 Entry Point (`__init__.py`)

#### Purpose

Registers services globally in `async_setup()` and initializes runtime components in
`async_setup_entry()`.

#### Design Rationale

Services are registered in `async_setup()` (called once at HA startup) rather than
`async_setup_entry()` (called per config entry). This ensures services remain available
even when a config entry is being reloaded. Each service handler resolves the active
config entry at invocation time via `_get_loaded_entry()`.

#### Key Abstractions

**Parameter Merging** — The `_get_param()` helper implements a three-tier fallback:

```
Service call data → ConfigEntry options → Hardcoded default
```

This allows every parameter to be overridden per-call while maintaining sensible global
defaults configurable through the UI.

**Runtime Data** — Uses the typed `LightControllerData` dataclass on
`ConfigEntry.runtime_data`, providing:

- Type-safe access to controller and preset manager
- Automatic cleanup when entry is unloaded
- No global state in `hass.data`

```python
@dataclass
class LightControllerData:
    controller: LightController
    preset_manager: PresetManager

type LightControllerConfigEntry = ConfigEntry[LightControllerData]
```

**Response Building** — The `_service_response()` helper constructs standardized
response dicts for all non-controller service responses (errors, preset operations,
create/delete results). It mirrors the `OperationResult.to_dict()` structure, ensuring a
consistent response schema regardless of whether the response originates from the
controller or a service handler.

**Optional String Helper** — `_get_optional_str()` retrieves optional string parameters,
treating empty strings as `None`. Used for parameters where the absence of a value is
semantically different from an empty string (e.g., effect names).

#### Service Schema Validation

All service inputs are validated through Voluptuous schemas at the HA service layer
boundary. Once data passes schema validation, internal code trusts it without redundant
checks.

### 4.2 Light Controller (`controller.py`)

#### Purpose

Implements the core control loop: expand entities → build targets → group by settings →
send commands → verify state → retry on failure.

#### Class Hierarchy

```
LightSettingsMixin          (shared to_service_data())
    ├── LightTarget         (single light + settings + state + transition)
    └── LightGroup          (multiple lights with identical settings)

TargetState (Enum)          ON | OFF
VerificationResult (Enum)   SUCCESS | WRONG_STATE | WRONG_BRIGHTNESS | WRONG_COLOR | UNAVAILABLE | ERROR
ColorTolerance (Dataclass)  brightness, rgb, kelvin tolerance values
RetryConfig (Dataclass)     retry parameters + delay calculation
OperationResult (Dataclass) complete operation result with to_dict()
```

#### Pipeline Design

The `ensure_state()` method implements a linear pipeline:

```
1. Input Validation
   │
   ├─ Validate entities (non-empty, correct type)
   └─ Parse target state string → TargetState enum
   │
2. Entity Expansion
   │
   ├─ _expand_entities() → for each entity:
   │   ├─ If has member entities → expand group
   │   ├─ If light.* → validate availability
   │   └─ Otherwise → skip with warning
   │
   └─ Deduplicate, separate valid/skipped
   │
3. Target Building
   │
   ├─ _build_targets() → LightTarget per entity
   │   ├─ Apply per-entity overrides from `targets` param
   │   └─ Fall back to default brightness/color/effect
   │
4. Command Dispatch (skip_verification=True path)
   │
   ├─ _send_commands_per_target() → fire and return
   │
5. Retry Loop (verification path)
   │
   ├─ While pending targets AND attempts < max AND time < max_runtime:
   │   ├─ Calculate delay (linear or exponential backoff)
   │   ├─ _send_commands_per_target() (transition on first attempt only)
   │   ├─ await asyncio.sleep(delay)
   │   ├─ _verify_light() for each target
   │   ├─ _build_dispatch_batches() → rebuild batch groupings
   │   └─ Filter at batch level: if ANY target in a batch failed,
   │      retry the ENTIRE batch (minus unavailable entities)
   │
6. Result Assembly
   │
   └─ Return OperationResult.to_dict()
```

#### Command Batching Strategy

Lights with identical settings are grouped to minimize service calls:

```
Input: [light.a(50%, 4000K), light.b(50%, 4000K), light.c(80%, RGB)]

Grouped:
  Group 1: [light.a, light.b] → brightness_pct=50, color_temp_kelvin=4000
  Group 2: [light.c]          → brightness_pct=80, rgb_color=[...]

Result: 2 service calls instead of 3
```

For ON targets, grouping uses a composite key of
`(brightness_pct, rgb_color, color_temp_kelvin, effect, transition)`. For OFF targets,
all entities are batched into a single `turn_off` call regardless of original settings.

#### Batch-Level Retry

During the retry loop, `_build_dispatch_batches()` reconstructs the batch groupings used
during dispatch. Verification is then applied at batch granularity: if **any** target in
a batch fails verification, the **entire batch** is re-sent (excluding unavailable
entities). This avoids sending partial groups, which could cause visual inconsistencies
when lights in the same batch should have identical settings.

#### Logbook Integration

`_log_to_logbook()` writes operation results to Home Assistant's logbook service.
Logbook entries are written for failures (always) and successes (when `log_success` is
enabled). Calls are non-blocking (`blocking=False`) to avoid delaying the response.

#### Verification Logic

Verification checks are layered:

1. **State check** — Is the light on/off as expected?
2. **Brightness check** — Is brightness within tolerance? (ON only)
3. **Color check** — Is RGB or Kelvin within tolerance? (ON only, if specified)

Color verification uses a tri-state result (`True`/`False`/`None`):

- `True` — Color matches within tolerance
- `False` — Color does not match
- `None` — Color mode not supported by this light (not a failure)

This prevents false failures for lights that don't support the requested color mode.

### 4.3 Preset Manager (`preset_manager.py`)

#### Purpose

Manages presets: creation, storage, retrieval, activation, and deletion. Lookup by ID or
name is provided via `find_preset()`, which first tries by ID then falls back to
case-insensitive name matching.

#### Storage Design

Presets are stored in `ConfigEntry.data["presets"]` as a dict keyed by UUID:

```python
{
    "presets": {
        "uuid-1": {
            "id": "uuid-1",
            "name": "Evening Ambiance",
            "entities": ["light.living_room", "light.lamp"],
            "state": "on",
            "brightness_pct": 40,
            "color_temp_kelvin": 2700,
            "targets": [
                {"entity_id": "light.living_room", "brightness_pct": 60},
                {"entity_id": "light.lamp", "brightness_pct": 20}
            ],
            "transition": 2.0,
            "skip_verification": false
        }
    }
}
```

Using `ConfigEntry.data` ensures:

- Persistence across HA restarts
- Automatic backup/restore with HA's configuration system
- No external file dependencies

#### Listener Pattern

PresetManager implements an observer pattern for entity platform synchronization:

```
PresetManager
    │
    ├── register_listener(callback) → returns unsubscribe()
    │
    ├── _notify_listeners() ← called on create/update/delete/status change
    │
    └── Listeners:
        ├── button.py::async_add_preset_buttons  (add new button entities)
        ├── sensor.py::async_add_preset_sensors   (add new sensor entities)
        ├── PresetButton::_handle_preset_update   (refresh entity state)
        └── PresetStatusSensor::_handle_preset_update (refresh entity state)
```

Entity platform setup functions register a top-level listener to create entities for new
presets. Individual entities also register their own listener to refresh state when
presets change.

#### Activation Delegation

`activate_preset_with_options()` bridges presets to the controller, merging preset
settings with ConfigEntry options for tolerances and retry behavior:

```python
async def activate_preset_with_options(
    self, preset: PresetConfig, controller: LightController, options: Mapping
) -> dict[str, Any]:
    return await controller.ensure_state(
        entities=preset.entities,
        state_target=preset.state,
        default_brightness_pct=preset.brightness_pct,
        # ... preset fields ...
        brightness_tolerance=options.get(CONF_BRIGHTNESS_TOLERANCE, DEFAULT_...),
        # ... options fields ...
    )
```

### 4.4 Config Flow (`config_flow.py`)

#### Purpose

Provides the UI for initial setup, settings management, and preset CRUD operations.

#### Flow Structure

```
ConfigFlow (initial setup)
    └── async_step_user → create entry with default options

OptionsFlow (ongoing management)
    └── async_step_init → menu
        ├── settings
        │   └── Collapsible sections: defaults, tolerances, retry, logging
        │
        ├── add_preset
        │   └── preset_entity_menu (hub)
        │       ├── select_entity_to_configure → configure_entity
        │       ├── add_more_entities
        │       ├── remove_entity
        │       └── save → _create_preset_from_data()
        │
        └── manage_presets → menu
            ├── edit_preset → (loads into preset_entity_menu)
            └── delete_preset → confirm_delete
```

#### Design Decisions

**Collapsible Sections** — Settings use HA's `section()` helper to group related
options. "Defaults" is expanded by default; "Tolerances", "Retry Settings", and
"Logging" are collapsed. This reduces visual complexity for common tasks.

**Hub-and-Spoke Preset Editing** — The `preset_entity_menu` step acts as a hub. From it,
users can configure entities, add more, remove some, or save. After each spoke action,
control returns to the hub. This allows iterative refinement without a rigid linear
wizard.

**Per-Entity Configuration** — Each light in a preset can have its own state,
brightness, color, and transition. This is stored during the flow as a dict keyed by
entity_id, then converted to a list format for storage.

### 4.5 Entity Platforms (`button.py`, `sensor.py`)

#### Button Platform

Each preset creates a `PresetButton` entity that:

- Activates the preset via `preset_manager.activate_preset_with_options()` on press
- Sets status to ACTIVATING before the call, then SUCCESS or FAILED after
- Exposes preset details as extra state attributes (entities, brightness, colors)
- Changes icon based on preset target state (on vs off)
- Reports as unavailable if its preset is deleted

#### Sensor Platform

Each preset creates a `PresetStatusSensor` entity that:

- Shows current status as an ENUM sensor: idle, activating, success, failed
- Exposes detailed activation results as extra state attributes
- Changes icon based on current status
- Reports as unavailable if its preset is deleted

#### Entity Lifecycle

```
async_setup_entry()
    │
    ├── Create initial entities for existing presets
    │
    └── Register listener with PresetManager
        │
        ├── On preset created → async_add_entities([new_entity])
        │
        └── On preset deleted → entity.available returns False
                                entity.async_write_ha_state() updates HA
```

The `added_preset_ids` set prevents duplicate entity creation when listeners fire for
status changes rather than new presets.

---

## 5. Data Design

### 5.1 Data Model

```
ConfigEntry
├── data
│   └── presets: dict[str, PresetDict]     # Persistent preset storage
├── options
│   ├── default_brightness_pct: int        # 1-100
│   ├── default_transition: float          # seconds
│   ├── brightness_tolerance: int          # ±%
│   ├── rgb_tolerance: int                 # ±0-255
│   ├── kelvin_tolerance: int              # ±K
│   ├── delay_after_send: float            # seconds
│   ├── max_retries: int                   # 1-10
│   ├── max_runtime_seconds: float         # seconds
│   ├── use_exponential_backoff: bool
│   ├── max_backoff_seconds: float         # seconds
│   └── log_success: bool
└── runtime_data: LightControllerData
    ├── controller: LightController
    └── preset_manager: PresetManager
        ├── _presets: dict[str, PresetConfig]   # In-memory copy
        ├── _status: dict[str, PresetStatus]    # Runtime-only status
        └── _listeners: list[Callable]          # Observer callbacks
```

### 5.2 Preset Data Schema

```python
PresetConfig:
    id: str                          # UUID v4
    name: str                        # User-facing name
    entities: list[str]              # Entity IDs (light.* or group.*)
    state: str                       # "on" or "off"
    brightness_pct: int              # 1-100, default 100
    rgb_color: list[int] | None      # [R, G, B] each 0-255
    color_temp_kelvin: int | None    # 1000-10000
    effect: str | None               # Effect name
    targets: list[dict]              # Per-entity overrides
    transition: float                # Seconds, default 0.0
    skip_verification: bool          # Fire-and-forget mode
```

### 5.3 Operation Result Schema

All service calls return a consistent result dictionary:

```python
{
    "success": bool,                 # Overall success
    "result": str,                   # "success" | "failed" | "timeout" | "error" | "no_valid_entities"
    "message": str,                  # Human-readable description
    "attempts": int,                 # Number of retry cycles
    "total_lights": int,             # Total expanded lights
    "failed_lights": list[str],      # Entity IDs that didn't reach target
    "skipped_lights": list[str],     # Unavailable entity IDs
    "elapsed_seconds": float         # Wall-clock time
}
```

### 5.4 Constants Organization

All constants are centralized in `const.py` with a clear naming convention:

| Prefix            | Purpose                     | Example                    |
| ----------------- | --------------------------- | -------------------------- |
| `CONF_*`          | ConfigEntry option keys     | `CONF_MAX_RETRIES`         |
| `DEFAULT_*`       | Default values              | `DEFAULT_MAX_RETRIES = 3`  |
| `ATTR_*`          | Service call parameter keys | `ATTR_MAX_RETRIES`         |
| `PRESET_*`        | Preset storage field keys   | `PRESET_BRIGHTNESS_PCT`    |
| `RESULT_*`        | Response dict keys          | `RESULT_FAILED_LIGHTS`     |
| `RESULT_CODE_*`   | Response result codes       | `RESULT_CODE_TIMEOUT`      |
| `SERVICE_*`       | Service names               | `SERVICE_ENSURE_STATE`     |
| `COLOR_MODE_*`    | Light color modes           | `COLOR_MODE_RGB`           |
| `PRESET_STATUS_*` | Preset runtime status       | `PRESET_STATUS_ACTIVATING` |

---

## 6. Interface Design

### 6.1 Service Interface

The integration exposes five services under the `ha_light_controller` domain:

#### `ensure_state`

The primary service. Controls lights with optional verification and retry.

**Input Parameters:** | Parameter | Type | Required | Default | Source |
|-----------|------|----------|---------|--------| | `entities` | `list[str]` | Yes | —
| Call data | | `state` | `"on"\|"off"` | No | `"on"` | Call data | | `brightness_pct` |
`int (1-100)` | No | Options/100 | Call → Options → Default | | `rgb_color` |
`[int,int,int]` | No | None | Call data | | `color_temp_kelvin` | `int (1000-10000)` |
No | None | Call data | | `effect` | `str` | No | None | Call data | | `targets` |
`list[dict]` | No | None | Call data | | `brightness_tolerance` | `int (0-50)` | No |
Options/3 | Call → Options → Default | | `rgb_tolerance` | `int (0-100)` | No |
Options/10 | Call → Options → Default | | `kelvin_tolerance` | `int (0-1000)` | No |
Options/150 | Call → Options → Default | | `transition` | `float (0-300)` | No |
Options/0 | Call → Options → Default | | `delay_after_send` | `float (0.1-60)` | No |
Options/2.0 | Call → Options → Default | | `max_retries` | `int (1-20)` | No | Options/3
| Call → Options → Default | | `max_runtime_seconds` | `float (5-600)` | No | Options/60
| Call → Options → Default | | `use_exponential_backoff` | `bool` | No | Options/false |
Call → Options → Default | | `max_backoff_seconds` | `float (1-300)` | No | Options/30 |
Call → Options → Default | | `skip_verification` | `bool` | No | `false` | Call data | |
`log_success` | `bool` | No | Options/false | Call → Options → Default |

#### `activate_preset`

Activates a saved preset by name or ID.

| Parameter | Type  | Required |
| --------- | ----- | -------- |
| `preset`  | `str` | Yes      |

#### `create_preset`

Creates a new preset programmatically.

| Parameter           | Type            | Required | Default |
| ------------------- | --------------- | -------- | ------- |
| `name`              | `str`           | Yes      | —       |
| `entities`          | `list[str]`     | Yes      | —       |
| `state`             | `"on"\|"off"`   | No       | `"on"`  |
| `brightness_pct`    | `int`           | No       | `100`   |
| `rgb_color`         | `[int,int,int]` | No       | None    |
| `color_temp_kelvin` | `int`           | No       | None    |
| `effect`            | `str`           | No       | None    |
| `targets`           | `list[dict]`    | No       | None    |
| `transition`        | `float`         | No       | `0`     |
| `skip_verification` | `bool`          | No       | `false` |

#### `delete_preset`

Deletes a preset by ID. Removes associated button and sensor entities from the entity
registry.

| Parameter   | Type  | Required |
| ----------- | ----- | -------- |
| `preset_id` | `str` | Yes      |

#### `create_preset_from_current`

Captures current light states into a new preset. Reads brightness, color, and effect
from each entity's current state.

| Parameter  | Type        | Required |
| ---------- | ----------- | -------- |
| `name`     | `str`       | Yes      |
| `entities` | `list[str]` | Yes      |

### 6.2 Entity Interface

#### Button Entity (`button.ha_light_controller_*`)

- **Action:** Pressing activates the associated preset
- **Attributes:** preset_id, entities, state, brightness_pct, rgb_color,
  color_temp_kelvin, effect, target_count, last_result, last_activated
- **Availability:** Tied to preset existence
- **Device:** Grouped under "Light Controller" device

#### Sensor Entity (`sensor.ha_light_controller_*_status`)

- **State:** ENUM — idle, activating, success, failed
- **Attributes:** preset_id, preset_name, target_state, entity_count, last_activated,
  last_success, last_message, last_attempts, last_elapsed, failed_lights, failed_count,
  skipped_lights, skipped_count
- **Availability:** Tied to preset existence
- **Device:** Grouped under "Light Controller" device

### 6.3 Config Flow Interface

#### Initial Setup

Single form step with default brightness and transition time. Creates the ConfigEntry.

#### Options Menu

Three-option menu:

1. **Settings** — Collapsible sections for defaults, tolerances, retry behavior, and
   logging
2. **Add Preset** — Multi-step wizard with per-entity configuration
3. **Manage Presets** — Sub-menu for editing or deleting existing presets

---

## 7. Behavioral Design

### 7.1 Ensure State — Verification Mode

```
┌─────────────┐
│ ensure_state │
│   called     │
└──────┬──────┘
       │
       ▼
┌──────────────┐     No     ┌─────────────┐
│ Entities     ├────────────► Return error │
│ provided?    │             └─────────────┘
└──────┬───────┘
       │ Yes
       ▼
┌──────────────┐
│ Expand &     │
│ deduplicate  │
└──────┬───────┘
       │
       ▼
┌──────────────┐     No     ┌─────────────────────┐
│ Valid lights ├────────────► Return               │
│ found?       │             │ no_valid_entities   │
└──────┬───────┘             └─────────────────────┘
       │ Yes
       ▼
┌──────────────┐
│ Build targets│
│ with         │
│ overrides    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     Yes    ┌──────────────┐
│ skip_        ├────────────► Send once,   │
│ verification?│             │ return       │
└──────┬───────┘             └──────────────┘
       │ No
       ▼
┌──────────────────────────────────────────┐
│              RETRY LOOP                  │
│                                          │
│  While pending AND attempt < max         │
│  AND elapsed < max_runtime:              │
│                                          │
│  1. Calculate delay                      │
│  2. Send commands (transition 1st only)  │
│  3. Sleep(delay)                         │
│  4. Verify each target                   │
│  5. Rebuild dispatch batches             │
│  6. For each batch: if ANY target failed │
│     → retry entire batch (skip unavail)  │
│  7. attempt++                            │
│                                          │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌────────┐ ┌────────┐
   │ Timeout │ │ Failed │ │Success │
   │         │ │        │ │        │
   │ return  │ │ return │ │ return │
   │ timeout │ │ failed │ │success │
   └─────────┘ └────────┘ └────────┘
```

### 7.2 Preset Activation Sequence

```
User presses preset button
    │
    ▼
PresetButton.async_press()
    │
    ├── Verify preset exists
    ├── Set status → ACTIVATING
    │
    ▼
preset_manager.activate_preset_with_options()
    │
    ├── Merge preset config with entry options
    │
    ▼
controller.ensure_state()
    │
    ├── (full pipeline as Section 7.1)
    │
    ▼
Return result
    │
    ├── success=True → status → SUCCESS
    └── success=False → status → FAILED
    │
    ▼
_notify_listeners()
    │
    ├── PresetStatusSensor refreshes state
    └── PresetButton refreshes attributes
```

### 7.3 Entity Expansion Behavior

| Input                                | Behavior                                                  |
| ------------------------------------ | --------------------------------------------------------- |
| `light.desk_lamp`                    | Direct inclusion if available                             |
| `light.living_room` (light group)    | Expand `entity_id` attribute to member lights             |
| `group.downstairs_lights` (HA group) | Expand `entity_id` attribute, keep only `light.*` members |
| `switch.outlet`                      | Skipped with warning (not a light domain)                 |
| Unavailable entity                   | Moved to `skipped_lights` list                            |

### 7.4 Retry Timing

With default settings (delay=2s, max_retries=3, no backoff):

```
t=0.0s  Send commands
t=2.0s  Verify → 2 still pending
t=2.0s  Resend
t=4.0s  Verify → 1 still pending
t=4.0s  Resend
t=6.0s  Verify → all success
```

With exponential backoff (delay=2s, max_retries=3, max_backoff=30s):

```
t=0.0s   Send commands
t=2.0s   Verify → retry needed
t=2.0s   Resend
t=6.0s   Verify → retry needed (delay was 2*2^1=4s)
t=6.0s   Resend
t=14.0s  Verify (delay was 2*2^2=8s)
```

---

## 8. Configuration and Deployment

### 8.1 Installation

The integration is distributed as a HACS custom repository. Installation copies the
`custom_components/ha_light_controller/` directory into the HA
`config/custom_components/` path.

### 8.2 Manifest

```json
{
  "domain": "ha_light_controller",
  "name": "Light Controller",
  "config_flow": true,
  "homeassistant": "2025.2.0",
  "iot_class": "calculated",
  "integration_type": "service",
  "requirements": [],
  "dependencies": ["light", "group"]
}
```

Key manifest decisions:

- **`iot_class: calculated`** — The integration doesn't communicate with external
  services; it computes state from HA's internal state machine.
- **`integration_type: service`** — It provides services, not a device or hub
  integration.
- **`requirements: []`** — No external PyPI dependencies. Uses only HA's built-in
  libraries.
- **`dependencies: ["light", "group"]`** — Ensures the light and group integrations are
  loaded before this integration.

### 8.3 Configuration Defaults

| Setting              | Default | Rationale                                           |
| -------------------- | ------- | --------------------------------------------------- |
| Brightness           | 100%    | Full brightness is the safest default               |
| Transition           | 0.0s    | Instant for predictable verification timing         |
| Brightness tolerance | ±3%     | Accounts for rounding in 0-255 → 0-100% conversion  |
| RGB tolerance        | ±10     | Accounts for color mode conversion artifacts        |
| Kelvin tolerance     | ±150K   | Accounts for device-level rounding                  |
| Delay after send     | 2.0s    | Gives Zigbee/Z-Wave time to execute and report back |
| Max retries          | 3       | Balances reliability with total runtime             |
| Max runtime          | 60s     | Hard timeout prevents runaway operations            |
| Exponential backoff  | Off     | Linear delay is simpler and works for most cases    |
| Max backoff          | 30s     | Cap prevents excessive wait between retries         |
| Log success          | Off     | Avoids logbook clutter by default                   |

### 8.4 CI/CD Pipeline

```
Push/PR to main or testing
    │
    ├── Lint (Ruff check + format check)
    ├── Type Check (mypy strict)
    ├── Test (pytest on Python 3.13 + 3.14)
    └── Verify Environment (script check)
    │
    └── All Checks gate job
```

---

## 9. Quality Attributes

### 9.1 Reliability

- **State verification** ensures commands were received and executed
- **Configurable retry** handles transient failures
- **Timeout protection** prevents infinite retry loops
- **Graceful degradation** — unavailable lights are skipped, not treated as failures

### 9.2 Performance

- **Concurrent command dispatch** — `asyncio.gather()` sends to all light groups in
  parallel
- **Command batching** — Lights with identical settings share a single service call
- **Transition on first attempt only** — Retries are instant for quick recovery
- **Non-blocking** — All I/O is async, never blocks HA's event loop

### 9.3 Maintainability

- **98.55% test coverage** (319 tests, branch coverage enabled)
- **Strict type checking** with mypy in strict mode
- **Ruff linting** with pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade
  rules
- **Constants centralization** — All magic values live in `const.py`
- **Clear separation** — Controller knows nothing about presets; PresetManager delegates
  to Controller

### 9.4 Extensibility

Adding a new service parameter requires changes to five files in a predictable pattern:

1. `const.py` — Add constant
2. `__init__.py` — Add to schema and handler
3. `services.yaml` — Add UI field definition
4. `controller.py` — Add to `ensure_state()` if behavior-relevant
5. `preset_manager.py` — Add to `activate_preset_with_options()` if preset-relevant

### 9.5 Integration Quality Scale Compliance

| Tier                                                    | Status      |
| ------------------------------------------------------- | ----------- |
| **Bronze** (config flow, basic tests, coding standards) | Achieved    |
| **Silver** (error handling, availability, logging)      | Achieved    |
| **Gold** (fully async, >80% coverage, type annotations) | Achieved    |
| **Platinum** (optimal performance, active maintenance)  | In progress |

---

## 10. Constraints and Assumptions

### 10.1 Home Assistant Constraints

| Constraint                             | Impact on Design                                                       |
| -------------------------------------- | ---------------------------------------------------------------------- |
| Single-threaded asyncio event loop     | All I/O must be async; no blocking calls allowed                       |
| RPi-class hardware target              | Efficient grouping and batching to minimize service calls              |
| No filesystem access outside `config/` | Presets stored in ConfigEntry, not files                               |
| Must use HA's service registry         | Cannot bypass `light.turn_on`; works through HA's abstraction layer    |
| Entity state is eventually consistent  | Verification delay (`delay_after_send`) accounts for state propagation |

### 10.2 Assumptions

1. **Lights report accurate state** — Verification depends on HA's state machine being
   up to date. If a device doesn't report state changes (e.g., dumb WiFi relay),
   verification will always fail.
2. **Groups have `entity_id` attribute** — Entity expansion relies on the `entity_id`
   attribute containing member entity IDs. This is true for HA light groups and group
   helper entities.
3. **Single config entry** — The integration expects at most one config entry.
   `_get_loaded_entry()` returns the first loaded entry.
4. **Color mode exclusivity** — RGB and color temperature are treated as mutually
   exclusive, matching how most lights operate (switching from RGB to CT or vice versa).

### 10.3 Known Limitations

1. **No real-time monitoring** — The integration verifies state after a fixed delay, not
   via state change events. This is simpler but means the delay must account for the
   slowest device.
2. **No per-light retry isolation** — If one light in a group fails, the entire group is
   re-sent. This is a trade-off for simpler batching logic.
3. **Preset editing replaces** — Editing a preset via config flow deletes the old preset
   and creates a new one with a different ID. Button and sensor entities are
   regenerated.

---

_This document reflects the implementation as of version 0.3.0 (February 2026)._
