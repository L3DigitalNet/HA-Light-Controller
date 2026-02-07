---
name: ha-quality-review
description: Review a Home Assistant integration against the Integration Quality Scale (IQS) and identify what tier it qualifies for (Bronze, Silver, Gold, Platinum). Use when the user says "review", "quality check", "ready for PR", "core submission", "quality scale", "IQS", or asks whether their integration meets Home Assistant standards. Also use before submitting to HACS or HA core.
disable-model-invocation: true
---

# Home Assistant Integration Quality Scale Review

Run this skill with `/ha-quality-review` to perform a systematic review of an integration against the official Integration Quality Scale.

## Review Process

Perform these steps in order:

### 1. Locate the Integration

Find all integration files. Check for `custom_components/*/manifest.json` or `homeassistant/components/*/manifest.json`.

### 2. Validate manifest.json

Required fields for any integration:
- `domain` — lowercase, underscores only, matches folder name
- `name` — human-readable name
- `codeowners` — list of GitHub usernames with `@` prefix
- `documentation` — valid URL
- `iot_class` — one of: `local_polling`, `local_push`, `cloud_polling`, `cloud_push`, `calculated`, `assumed_state`
- `integration_type` — one of: `hub`, `device`, `service`, `virtual`, `helper`, `hardware`, `system`, `entity`

Required for custom integrations:
- `version` — SemVer format (e.g., `1.0.0`)

Required for config-flow integrations:
- `config_flow: true`

### 3. Score Against Each Tier

#### Bronze Tier Checklist (Minimum for Core)

Check each item and report pass/fail:

- [ ] **Config flow exists** — `config_flow.py` is present and `config_flow: true` in manifest
- [ ] **Async setup** — `async_setup_entry` and `async_unload_entry` in `__init__.py`
- [ ] **Platform forwarding** — Uses `async_forward_entry_setups` (not deprecated `async_setup_platforms`)
- [ ] **Unique IDs** — Every entity has a `unique_id` property or `_attr_unique_id`
- [ ] **Entity names** — `_attr_has_entity_name = True` set on entity classes
- [ ] **Device info** — Entities provide `device_info` with stable `identifiers`
- [ ] **Type hints** — Function signatures have type annotations
- [ ] **Modern imports** — Uses `from __future__ import annotations`, modern syntax (`list[str]` not `List[str]`)
- [ ] **Constants file** — `const.py` exists with `DOMAIN` defined
- [ ] **Strings** — `strings.json` exists with all config flow step/error/abort keys
- [ ] **Translations** — `translations/en.json` exists (can be copy of strings.json)
- [ ] **No YAML config** — No `async_setup_platform` or YAML-only configuration paths
- [ ] **Tests exist** — At minimum, config flow tests covering success, connect failure, auth failure

#### Silver Tier Checklist (Reliability)

- [ ] **DataUpdateCoordinator** — Uses coordinator for polling (not manual timers)
- [ ] **Error handling** — `UpdateFailed` raised for temporary errors, `ConfigEntryAuthFailed` for auth
- [ ] **Availability** — Entities inherit `CoordinatorEntity` for automatic availability, custom `available` property if needed
- [ ] **Reauth flow** — `async_step_reauth` implemented in config flow
- [ ] **Options flow** — Configurable settings (polling interval, etc.) via options flow
- [ ] **Unload cleanup** — `async_unload_entry` properly cleans up all resources
- [ ] **Log-once pattern** — Uses coordinator logging (no repeated error logs per poll cycle)
- [ ] **Data descriptions** — `data_description` in strings.json for config flow fields

#### Gold Tier Checklist (Feature Complete)

- [ ] **Full async** — No blocking I/O anywhere; all sync calls wrapped in `async_add_executor_job`
- [ ] **Comprehensive tests** — Config flow, setup, unload, entity state, and error path tests
- [ ] **Type coverage** — Complete type annotations, passes `mypy --strict` or close to it
- [ ] **always_update=False** — Coordinator uses `always_update=False` when data supports `__eq__`
- [ ] **runtime_data** — Uses `entry.runtime_data` instead of `hass.data[DOMAIN]`
- [ ] **Entity descriptions** — Uses `EntityDescription` dataclasses for declarative entity definitions
- [ ] **Diagnostics** — Implements `diagnostics.py` for troubleshooting data export
- [ ] **Library separation** — Device communication in separate PyPI package

#### Platinum Tier Checklist (Exemplary)

- [ ] **Discovery** — Supports SSDP, mDNS/Zeroconf, DHCP, or USB discovery
- [ ] **100% test coverage** — All code paths tested
- [ ] **Reconfiguration** — Config entries can be reconfigured without remove/re-add
- [ ] **Dynamic entities** — Entities added/removed as devices appear/disappear
- [ ] **Repair issues** — Uses `homeassistant.helpers.issue_registry` for actionable user issues

### 4. Generate Report

Output a structured report:

```
## Integration Quality Review: {domain}

### Tier Assessment
- Bronze: {PASS/FAIL} ({X}/{Y} checks passed)
- Silver: {PASS/FAIL} ({X}/{Y} checks passed)
- Gold:   {PASS/FAIL} ({X}/{Y} checks passed)
- Platinum: {PASS/FAIL} ({X}/{Y} checks passed)

**Current Tier: {highest passing tier}**

### Critical Issues (Must Fix)
1. [Issue with specific file:line reference and fix]

### Recommended Improvements
1. [Improvement with code example]

### Positive Findings
- [Things done well]

### Path to Next Tier
To reach {next tier}, address these items:
1. [Prioritized action item]
```

### 5. Provide Fixes

For every failing check, provide a specific code fix showing the before (problematic) and after (correct) pattern. Reference the relevant skills for detailed guidance:

- Config flow issues → see `ha-config-flow` skill
- Coordinator issues → see `ha-coordinator` skill
- Entity issues → see `ha-entity-platforms` skill
- Async issues → see `ha-async-patterns` skill
- Test issues → see `ha-testing` skill
