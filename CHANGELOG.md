# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2026-02-14

### Fixed

- Handle non-string entity IDs in entity expansion
- Config flow typing and lint issues
- Typing and lint issues for light controller services

### Changed

- Updated documentation for v0.2.1 release
- Updated contributor documentation with current tooling and versions
- Updated core instruction files to reflect current environment

### Added

- Skills for Home Assistant integration development
- Link verification tooling and report
- uv.lock file for package management

## [0.2.1] - 2026-02-07

### Added

- Per-entity state and transition support in presets
- Mixed on/off states in single preset (e.g., turn some lights on, others off)
- Per-entity transition times with fallback to global preset transition
- `_send_commands_per_target()` method for handling mixed-state presets

### Changed

- Updated Python requirement to 3.14.2 (Home Assistant 2025.2.0+)
- Updated minimum Home Assistant version to 2025.2.0
- Improved documentation clarity and removed early beta disclaimer
- Preset creation now derives preset-level state/transition from per-entity configs

### Fixed

- Preset configuration gaps where UI-collected per-entity settings were not used by
  backend
- Hardcoded `state="on"` and `transition=0.0` in preset creation
- Minor bug fixes and stability improvements

## [0.2.0] - 2026-01-31

### Removed

- Notification feature (`notify_on_failure` parameter)
- Blueprint automation templates (adaptive_lighting, button_scene_controller,
  motion_activated_scene, scene_scheduler)

### Changed

- Simplified scope to focus on core light control and preset management
- Updated documentation to reflect current feature set

### Notes

This release removes features that were not essential to the core functionality. Users
requiring notifications can implement them via automations triggered by service
responses. The core ensure_state service and preset management remain fully functional.

## [0.1.3] - 2026-01-31

- Previous release (see git history)
