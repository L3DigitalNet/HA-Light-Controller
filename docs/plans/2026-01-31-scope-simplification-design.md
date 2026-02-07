# Scope Simplification Plan
**Date**: 2026-01-31
**Status**: ✅ **COMPLETED** (Design → Execution → Release)
**Goal**: Simplify project scope to core functionality (light control + presets + UI)

> ✅ **IMPLEMENTATION COMPLETE** - Released as v0.2.0 (2026-01-31)
>
> This design document guided the scope simplification that resulted in v0.2.0. All phases were completed:
> - ✅ Phase 1: Feature Removal (notification system and blueprints)
> - ✅ Phase 2: Best Practices Verification
> - ✅ Phase 3: Testing & Validation
> - ✅ Phase 4: Documentation Updates
> - ✅ Phase 5: Release Preparation
>
> **See:** `2026-01-31-remove-notifications-and-blueprints.md` for detailed implementation plan
>
> **Result:** Integration now focuses exclusively on core light control with verification/retry and preset management.

## Current State Assessment

### Codebase Metrics
- **Total Lines**: 3,241 lines across 7 Python files
- **Test Coverage**: 5,248 lines of tests across 6 test files
- **Complexity Areas**:
  - `config_flow.py`: 973 lines (UI configuration)
  - `controller.py`: 812 lines (core logic)
  - `__init__.py`: 512 lines (service registration)

### Features Currently Implemented
✅ Core light control with verification/retry
✅ Preset management (CRUD operations)
✅ Config flow UI with collapsible sections
✅ Button/sensor entities for presets
✅ Exponential backoff retry strategy
❌ Notification system (`notify_on_failure`) - **TO REMOVE**
❌ Blueprint automations (4 files) - **TO REMOVE**

## Scope Definition

### Essential Features (Keep)
1. **Core Light Control**: `ensure_state` service with verification and retry
2. **Preset Management**: Create, activate, delete presets
3. **UI Configuration**: Config flow for settings and preset management
4. **Preset Entities**: Button and sensor entities for each preset
5. **Retry Strategies**: Both fixed delay and exponential backoff

### Features to Remove
1. **Notification System**: `notify_on_failure` parameter and related code
2. **Blueprint Automations**: All 4 blueprint YAML files

## Implementation Plan

### Phase 1: Feature Removal (2-3 hours)

#### Task 1.1: Remove Notification Feature
**Files to modify**:
- `custom_components/ha_light_controller/const.py`
  - Remove: `CONF_NOTIFY_ON_FAILURE`, `ATTR_NOTIFY_ON_FAILURE`
- `custom_components/ha_light_controller/controller.py`
  - Remove: `notify_on_failure` parameter from `ensure_state()`
  - Remove: `_send_notification()` method (lines 544-561)
  - Remove: 2 calls to `_send_notification()` (lines 754-756, 778-780)
- `custom_components/ha_light_controller/__init__.py`
  - Remove: `CONF_NOTIFY_ON_FAILURE`, `ATTR_NOTIFY_ON_FAILURE` imports
  - Remove: `ATTR_NOTIFY_ON_FAILURE` from service schema (line 182)
  - Remove: `notify_on_failure` parameter handling (line 262)
  - Remove: `notify_on_failure` from `ensure_state` call (line 284)
- `custom_components/ha_light_controller/config_flow.py`
  - Remove: `CONF_NOTIFY_ON_FAILURE` import and all references (lines 32, 115, 192-193, 363-364)
- `custom_components/ha_light_controller/preset_manager.py`
  - Remove: `CONF_NOTIFY_ON_FAILURE` import (line 27)
  - Remove: `notify_on_failure` parameter pass-through (line 423)
- `custom_components/ha_light_controller/services.yaml`
  - Remove: `notify_on_failure` field definition (line 183+)
- `custom_components/ha_light_controller/strings.json`
  - Remove: `notify_on_failure` entries (lines 90, 94, 286+)
- `custom_components/ha_light_controller/translations/en.json`
  - Remove: `notify_on_failure` entries (lines 90, 94, 286+)

**Tests to remove/update**:
- `tests/test_init.py::test_ensure_state_uses_config_notify_on_failure` - DELETE
- `tests/test_config_flow.py::test_step_settings_empty_notify` - DELETE
- Any other tests asserting on `notify_on_failure` behavior

**Verification**:
```bash
# Ensure no remaining references
grep -r "notify_on_failure\|NOTIFY_ON_FAILURE" custom_components/
grep -r "notify_on_failure" tests/

# Should return no results
```

#### Task 1.2: Remove Blueprints
**Actions**:
```bash
# Delete entire blueprints directory
rm -rf custom_components/ha_light_controller/blueprints/

# Verify deletion
ls -la custom_components/ha_light_controller/
```

**Documentation updates**:
- `README.md`: Remove "Blueprints" section (lines 107-115)
- `USAGE.md`: Remove blueprints references from TOC and content

**Verification**:
```bash
# Ensure no remaining references
grep -ri "blueprint" . --exclude-dir=.git
```

### Phase 2: Best Practices Verification (1-2 hours)

Based on [Home Assistant Developer Documentation](https://developers.home-assistant.io/):

#### Task 2.1: Manifest Compliance
**Current**: `manifest.json` already compliant ✅
- Has required `version` field (0.1.3)
- Has `integration_type: service` ✅
- Has `iot_class: calculated` ✅
- Has `config_flow: true` ✅
- Dependencies correctly listed: `["light", "group"]` ✅

**Action**: Update version to `0.2.0` after simplification

#### Task 2.2: Service Registration Review
**Current state**: Services registered in `async_setup_entry()` ✅
**Best practice**: Services should be registered at integration level (see [Service docs](https://developers.home-assistant.io/docs/dev_101_services))

**Finding**: Current implementation is correct for integration-level services tied to a config entry.

#### Task 2.3: Code Quality Standards
**Criteria** (from [Quality Scale](https://www.home-assistant.io/docs/quality_scale/)):
- ✅ UI setup (config flow exists)
- ✅ Basic coding standards (follows HA patterns)
- ✅ Automated tests (comprehensive test suite)
- ⚠️  User documentation (good but could improve examples)

**Actions**:
- Verify all service schemas in `services.yaml` are accurate
- Ensure type hints are complete (already appear comprehensive)
- Add docstrings where missing

#### Task 2.4: Async Best Practices
**Check for**:
- All I/O operations are async ✅ (verified in controller.py)
- No blocking calls in event loop ✅
- Proper use of `asyncio.sleep()` vs `time.sleep()` ✅

### Phase 3: Testing & Validation (1-2 hours)

#### Task 3.1: Update Test Suite
1. Remove notification-related tests (identified in Phase 1)
2. Verify remaining tests pass:
   ```bash
   pytest tests/ -v
   ```
3. Check test coverage:
   ```bash
   pytest --cov=custom_components/ha_light_controller --cov-report=term-missing
   ```
4. Target: Maintain >80% coverage after removals

#### Task 3.2: Integration Testing
Manual verification checklist:
- [ ] Install integration via HACS custom repo
- [ ] Configure via UI (Settings → Integrations)
- [ ] Test `ensure_state` service with various light configurations
- [ ] Create preset via UI
- [ ] Activate preset via button entity
- [ ] Edit preset via options flow
- [ ] Delete preset with confirmation
- [ ] Verify all config options apply correctly

### Phase 4: Documentation Updates (30-60 minutes)

#### Task 4.1: Update README.md
- Remove "Blueprints" section
- Remove `notify_on_failure` from examples
- Update feature list to reflect current scope
- Bump version references to 0.2.0

#### Task 4.2: Update USAGE.md
- Remove blueprint references from TOC
- Remove "Blueprints" section
- Remove `notify_on_failure` from service documentation
- Update configuration options table

#### Task 4.3: Update CLAUDE.md
- Document the simplified scope
- Update service parameter list (remove notify_on_failure)
- Add note about removed features (for historical context)

### Phase 5: Release Preparation (30 minutes)

#### Task 5.1: Version Bump
- Update `manifest.json`: `"version": "0.2.0"`
- Create git tag: `v0.2.0`

#### Task 5.2: Changelog
Create `CHANGELOG.md`:
```markdown
# Changelog

## [0.2.0] - 2026-01-31

### Removed
- Notification feature (`notify_on_failure` parameter)
- Blueprint automation templates (4 files)

### Changed
- Simplified scope to focus on core light control and preset management

### Notes
This release removes features that were not essential to the core
functionality. Users relying on notifications can implement them
via automations triggered by service responses.
```

#### Task 5.3: Git Workflow
**Per project policy**:
- All changes on `testing` branch
- Do NOT push to `main` without permission
- Create PR when ready for review

## Success Criteria

### Functional Requirements
- ✅ Core `ensure_state` service works with all existing parameters (minus notify_on_failure)
- ✅ Preset CRUD operations function correctly
- ✅ Config flow UI for settings and presets works
- ✅ Button/sensor entities for presets work
- ✅ Exponential backoff retry strategy functions

### Quality Requirements
- ✅ All tests pass
- ✅ Test coverage >80%
- ✅ No lingering references to removed features
- ✅ Documentation accurate and complete
- ✅ Manifest.json compliant with HA standards

### Code Quality
- ✅ No `# TODO` or commented-out code
- ✅ Type hints complete
- ✅ Follows HA coding standards
- ✅ Follows project code principles (readability, simplicity)

## Risk Assessment

### Low Risk
- Removing blueprints: Self-contained, no code dependencies
- Removing notification tests: Clean isolation

### Medium Risk
- Notification feature removal: Touches 9 files, but well-isolated
- Mitigation: Comprehensive grep search before/after, thorough testing

### Dependencies
- No external dependencies changed
- No breaking changes to core services (only removed optional parameter)

## Timeline Estimate

**Total**: 5-8 hours of focused work

| Phase | Time | Parallelizable? |
|-------|------|-----------------|
| Phase 1: Feature Removal | 2-3h | No (sequential) |
| Phase 2: Best Practices | 1-2h | Yes (review only) |
| Phase 3: Testing | 1-2h | No (depends on Phase 1) |
| Phase 4: Documentation | 0.5-1h | Yes (during testing) |
| Phase 5: Release Prep | 0.5h | No (final step) |

## References

- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://www.home-assistant.io/docs/quality_scale/)
- [Service Development Guide](https://developers.home-assistant.io/docs/dev_101_services)
- [Creating Integration Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest)
- [Modern HA Integration Blueprint](https://github.com/jpawlowski/hacs.integration_blueprint)

## Next Steps

1. **User Approval**: Review and approve this plan
2. **Branch Setup**: Create `simplify-scope` branch from `testing`
3. **Execution**: Follow phases sequentially
4. **Review**: PR to `testing` branch when complete
5. **Validation**: Test in real HA environment before merging to `main`
