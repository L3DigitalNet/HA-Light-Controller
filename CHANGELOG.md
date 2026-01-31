# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-31

### Removed
- Notification feature (`notify_on_failure` parameter)
- Blueprint automation templates (adaptive_lighting, button_scene_controller, motion_activated_scene, scene_scheduler)

### Changed
- Simplified scope to focus on core light control and preset management
- Updated documentation to reflect current feature set

### Notes
This release removes features that were not essential to the core functionality.
Users requiring notifications can implement them via automations triggered by
service responses. The core ensure_state service and preset management remain
fully functional.

## [0.1.3] - 2026-01-31
- Previous release (see git history)
