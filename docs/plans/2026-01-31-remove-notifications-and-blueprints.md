# Remove Notifications and Blueprints Implementation Plan

> ✅ **STATUS: COMPLETED** - Implemented in v0.2.0 (2026-01-31)
>
> This plan was fully executed, resulting in the removal of the notification feature and
> all blueprint automation templates. All 18 tasks were completed successfully.
>
> **Verification:**
>
> - ✅ No references to `notify_on_failure` or `NOTIFY_ON_FAILURE` remain in codebase
> - ✅ Blueprints directory deleted
> - ✅ Tests updated and passing
> - ✅ Documentation updated (README.md, USAGE.md, CLAUDE.md)
> - ✅ Version bumped to 0.2.0
> - ✅ CHANGELOG.md created
>
> **See:** CHANGELOG.md v0.2.0 for summary of changes

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task.

**Goal:** Remove notification feature and blueprint automations to simplify scope to
core functionality

**Architecture:** Systematically remove notify_on_failure parameter and
\_send_notification() method from all 9 files, delete blueprints directory, update tests
and documentation

**Tech Stack:** Home Assistant custom integration, Python 3.12, pytest

---

## Task 1: Remove notification constants from const.py

**Files:**

- Modify: `custom_components/ha_light_controller/const.py:32-33,67`

**Step 1: Read current const.py to identify exact lines**

Run: `grep -n "NOTIFY_ON_FAILURE" custom_components/ha_light_controller/const.py`
Expected: Shows line numbers for CONF_NOTIFY_ON_FAILURE and ATTR_NOTIFY_ON_FAILURE

**Step 2: Remove notification constants**

Edit `custom_components/ha_light_controller/const.py`:

- Remove line with `CONF_NOTIFY_ON_FAILURE: Final = "notify_on_failure"`
- Remove line with `ATTR_NOTIFY_ON_FAILURE: Final = "notify_on_failure"`

**Step 3: Verify removal**

Run: `grep -n "NOTIFY_ON_FAILURE" custom_components/ha_light_controller/const.py`
Expected: No output (empty result)

**Step 4: Commit**

```bash
git add custom_components/ha_light_controller/const.py
git commit -m "refactor: remove notification constants from const.py

Remove CONF_NOTIFY_ON_FAILURE and ATTR_NOTIFY_ON_FAILURE constants
as part of notification feature removal.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Remove \_send_notification method from controller.py

**Files:**

- Modify:
  `custom_components/ha_light_controller/controller.py:544-561,587,754-756,778-780`

**Step 1: Read \_send_notification method**

Run: `sed -n '544,561p' custom_components/ha_light_controller/controller.py` Expected:
Shows the complete \_send_notification method

**Step 2: Remove \_send_notification method**

Edit `custom_components/ha_light_controller/controller.py`:

- Delete lines 544-561 (entire \_send_notification method including docstring)

**Step 3: Remove notify_on_failure parameter from ensure_state signature**

Edit `custom_components/ha_light_controller/controller.py` around line 587:

- Remove the line: `notify_on_failure: str | None = None,`

**Step 4: Remove first notification call (around line 754)**

Edit `custom_components/ha_light_controller/controller.py`:

- Remove the if block:

```python
if notify_on_failure:
    await self._send_notification(
        notify_on_failure, "Light Controller Timeout", message
    )
```

**Step 5: Remove second notification call (around line 778)**

Edit `custom_components/ha_light_controller/controller.py`:

- Remove the if block:

```python
if notify_on_failure:
    await self._send_notification(
        notify_on_failure, "Light Controller Failed", message
    )
```

**Step 6: Verify no notification references remain**

Run:
`grep -n "notify_on_failure\|_send_notification" custom_components/ha_light_controller/controller.py`
Expected: No output

**Step 7: Commit**

```bash
git add custom_components/ha_light_controller/controller.py
git commit -m "refactor: remove notification feature from controller

- Remove _send_notification() method
- Remove notify_on_failure parameter from ensure_state()
- Remove notification calls on timeout and failure

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Remove notification imports and schema from **init**.py

**Files:**

- Modify: `custom_components/ha_light_controller/__init__.py:37,70,182,262,284`

**Step 1: Remove notification constant imports**

Edit `custom_components/ha_light_controller/__init__.py`:

- Remove `CONF_NOTIFY_ON_FAILURE,` from imports (around line 37)
- Remove `ATTR_NOTIFY_ON_FAILURE,` from imports (around line 70)

**Step 2: Remove notification from service schema**

Edit `custom_components/ha_light_controller/__init__.py` around line 182:

- Remove line: `vol.Optional(ATTR_NOTIFY_ON_FAILURE): cv.string,`

**Step 3: Remove notification parameter extraction**

Edit `custom_components/ha_light_controller/__init__.py` around line 262:

- Remove line:
  `notify_on_failure = _get_optional_str(data, options, ATTR_NOTIFY_ON_FAILURE, CONF_NOTIFY_ON_FAILURE)`

**Step 4: Remove notification from ensure_state call**

Edit `custom_components/ha_light_controller/__init__.py` around line 284:

- Remove line: `notify_on_failure=notify_on_failure,`

**Step 5: Verify removal**

Run:
`grep -n "notify_on_failure\|NOTIFY_ON_FAILURE" custom_components/ha_light_controller/__init__.py`
Expected: No output

**Step 6: Commit**

```bash
git add custom_components/ha_light_controller/__init__.py
git commit -m "refactor: remove notification handling from service registration

- Remove notification constant imports
- Remove notification from service schema
- Remove notification parameter extraction and passing

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Remove notification references from config_flow.py

**Files:**

- Modify: `custom_components/ha_light_controller/config_flow.py:32,115,192-193,363-364`

**Step 1: Remove notification import**

Edit `custom_components/ha_light_controller/config_flow.py`:

- Remove `CONF_NOTIFY_ON_FAILURE,` from imports (line 32)

**Step 2: Remove notification from initial setup options**

Edit `custom_components/ha_light_controller/config_flow.py` around line 115:

- Remove line: `CONF_NOTIFY_ON_FAILURE: user_input.get(CONF_NOTIFY_ON_FAILURE, ""),`

**Step 3: Remove notification empty string handling**

Edit `custom_components/ha_light_controller/config_flow.py` around lines 192-193:

- Remove the if block:

```python
if not flat_options.get(CONF_NOTIFY_ON_FAILURE):
    flat_options[CONF_NOTIFY_ON_FAILURE] = ""
```

**Step 4: Remove notification field from settings schema**

Edit `custom_components/ha_light_controller/config_flow.py` around lines 363-364:

- Remove the vol.Optional block for CONF_NOTIFY_ON_FAILURE with its selector

**Step 5: Verify removal**

Run:
`grep -n "notify_on_failure\|NOTIFY_ON_FAILURE" custom_components/ha_light_controller/config_flow.py`
Expected: No output

**Step 6: Commit**

```bash
git add custom_components/ha_light_controller/config_flow.py
git commit -m "refactor: remove notification config from config flow

- Remove notification import and constant
- Remove notification field from setup and settings UI
- Remove empty string handling for notification field

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Remove notification from preset_manager.py

**Files:**

- Modify: `custom_components/ha_light_controller/preset_manager.py:27,423`

**Step 1: Remove notification import**

Edit `custom_components/ha_light_controller/preset_manager.py`:

- Remove `CONF_NOTIFY_ON_FAILURE,` from imports (line 27)

**Step 2: Remove notification parameter from activate call**

Edit `custom_components/ha_light_controller/preset_manager.py` around line 423:

- Remove line: `notify_on_failure=options.get(CONF_NOTIFY_ON_FAILURE),`

**Step 3: Verify removal**

Run:
`grep -n "notify_on_failure\|NOTIFY_ON_FAILURE" custom_components/ha_light_controller/preset_manager.py`
Expected: No output

**Step 4: Commit**

```bash
git add custom_components/ha_light_controller/preset_manager.py
git commit -m "refactor: remove notification from preset manager

Remove notification import and parameter pass-through in
activate_preset_with_options().

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Remove notification field from services.yaml

**Files:**

- Modify: `custom_components/ha_light_controller/services.yaml:183+`

**Step 1: Find notification field definition**

Run:
`grep -n -A5 "notify_on_failure:" custom_components/ha_light_controller/services.yaml`
Expected: Shows the field definition with name, description, selector

**Step 2: Remove notification field**

Edit `custom_components/ha_light_controller/services.yaml`:

- Remove the entire `notify_on_failure:` field definition block (typically 5-7 lines)

**Step 3: Verify removal**

Run: `grep -n "notify_on_failure" custom_components/ha_light_controller/services.yaml`
Expected: No output

**Step 4: Commit**

```bash
git add custom_components/ha_light_controller/services.yaml
git commit -m "refactor: remove notification field from services.yaml

Remove notify_on_failure field definition from ensure_state service.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Remove notification from strings.json

**Files:**

- Modify: `custom_components/ha_light_controller/strings.json:90,94,286+`

**Step 1: Find notification strings**

Run: `grep -n "notify_on_failure" custom_components/ha_light_controller/strings.json`
Expected: Shows 3+ occurrences

**Step 2: Remove notification strings**

Edit `custom_components/ha_light_controller/strings.json`:

- Remove all `"notify_on_failure"` entries (typically in config options and service
  fields)
- Ensure JSON remains valid after removal (check commas)

**Step 3: Validate JSON**

Run:
`python3 -m json.tool custom_components/ha_light_controller/strings.json > /dev/null`
Expected: No output (valid JSON)

**Step 4: Verify removal**

Run: `grep -n "notify_on_failure" custom_components/ha_light_controller/strings.json`
Expected: No output

**Step 5: Commit**

```bash
git add custom_components/ha_light_controller/strings.json
git commit -m "refactor: remove notification strings from strings.json

Remove notify_on_failure UI strings from config and service fields.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Remove notification from translations/en.json

**Files:**

- Modify: `custom_components/ha_light_controller/translations/en.json:90,94,286+`

**Step 1: Find notification translations**

Run:
`grep -n "notify_on_failure" custom_components/ha_light_controller/translations/en.json`
Expected: Shows 3+ occurrences

**Step 2: Remove notification translations**

Edit `custom_components/ha_light_controller/translations/en.json`:

- Remove all `"notify_on_failure"` entries
- Ensure JSON remains valid after removal (check commas)

**Step 3: Validate JSON**

Run:
`python3 -m json.tool custom_components/ha_light_controller/translations/en.json > /dev/null`
Expected: No output (valid JSON)

**Step 4: Verify removal**

Run:
`grep -n "notify_on_failure" custom_components/ha_light_controller/translations/en.json`
Expected: No output

**Step 5: Commit**

```bash
git add custom_components/ha_light_controller/translations/en.json
git commit -m "refactor: remove notification from English translations

Remove notify_on_failure translation strings.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Remove notification tests

**Files:**

- Modify: `tests/test_init.py` (remove test_ensure_state_uses_config_notify_on_failure)
- Modify: `tests/test_config_flow.py` (remove test_step_settings_empty_notify)

**Step 1: Find notification tests**

Run: `grep -n "def test.*notify" tests/test_init.py tests/test_config_flow.py` Expected:
Shows test function definitions

**Step 2: Remove test from test_init.py**

Edit `tests/test_init.py`:

- Delete entire `test_ensure_state_uses_config_notify_on_failure` function

**Step 3: Remove test from test_config_flow.py**

Edit `tests/test_config_flow.py`:

- Delete entire `test_step_settings_empty_notify` function

**Step 4: Verify removal**

Run: `grep -n "notify_on_failure" tests/` Expected: No output or only in preset_manager
test (listener exception test)

**Step 5: Run tests to ensure they still pass**

Run: `pytest tests/test_init.py tests/test_config_flow.py -v` Expected: All tests pass

**Step 6: Commit**

```bash
git add tests/test_init.py tests/test_config_flow.py
git commit -m "test: remove notification-related tests

Remove test_ensure_state_uses_config_notify_on_failure and
test_step_settings_empty_notify as notification feature is removed.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Verify no notification references remain

**Files:**

- None (verification only)

**Step 1: Search for notification in custom_components**

Run:
`grep -r "notify_on_failure\|NOTIFY_ON_FAILURE" custom_components/ha_light_controller/`
Expected: No output

**Step 2: Search for notification in tests**

Run: `grep -r "notify_on_failure" tests/` Expected: Only result should be
`tests/test_preset_manager.py::test_notify_listener_exception` (unrelated)

**Step 3: Search for \_send_notification**

Run: `grep -r "_send_notification" custom_components/` Expected: No output

**Step 4: Document verification**

No commit needed - verification step only.

---

## Task 11: Delete blueprints directory

**Files:**

- Delete: `custom_components/ha_light_controller/blueprints/` (entire directory)

**Step 1: Verify blueprints exist**

Run:
`ls -la custom_components/ha_light_controller/blueprints/automation/ha_light_controller/`
Expected: Shows 4 YAML files (adaptive_lighting, button_scene_controller,
motion_activated_scene, scene_scheduler)

**Step 2: Delete blueprints directory**

Run: `rm -rf custom_components/ha_light_controller/blueprints/`

**Step 3: Verify deletion**

Run: `ls custom_components/ha_light_controller/blueprints/ 2>&1` Expected: "No such file
or directory"

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: remove blueprint automations

Delete all 4 blueprint YAML files as they are not part of core scope:
- adaptive_lighting.yaml
- button_scene_controller.yaml
- motion_activated_scene.yaml
- scene_scheduler.yaml

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Update README.md

**Files:**

- Modify: `README.md` (remove Blueprints section, update examples)

**Step 1: Read current README**

Run: `grep -n "Blueprints\|notify_on_failure" README.md` Expected: Shows line numbers
for sections to modify

**Step 2: Remove notify_on_failure from examples**

Edit `README.md`:

- Find example around line 68 with `notify_on_failure: "notify.mobile_app_phone"`
- Remove that line from the example

**Step 3: Remove Blueprints section**

Edit `README.md`:

- Remove lines 107-115 (Blueprints section including table)

**Step 4: Update feature list**

Edit `README.md` around line 36:

- Remove line: `- **Blueprints** - Pre-built automation templates for common patterns`

**Step 5: Verify no blueprint/notification references**

Run: `grep -n "blueprint\|notify_on_failure" README.md` Expected: Only lowercase
"blueprint" in HACS context may remain, no notify_on_failure

**Step 6: Commit**

```bash
git add README.md
git commit -m "docs: update README to reflect removed features

- Remove notify_on_failure from usage examples
- Remove Blueprints section
- Update feature list

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Update USAGE.md

**Files:**

- Modify: `USAGE.md` (remove Blueprints section from TOC and content)

**Step 1: Find blueprint references**

Run: `grep -n -i "blueprint" USAGE.md` Expected: Shows TOC entry and Blueprints section

**Step 2: Remove from Table of Contents**

Edit `USAGE.md`:

- Remove `- [Blueprints](#blueprints)` from TOC (around line 15)

**Step 3: Remove Blueprints section**

Edit `USAGE.md`:

- Remove entire Blueprints section (find with grep result from step 1)

**Step 4: Verify removal**

Run: `grep -i "blueprint" USAGE.md` Expected: No output

**Step 5: Commit**

```bash
git add USAGE.md
git commit -m "docs: remove blueprints from USAGE.md

Remove Blueprints section and TOC entry.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Update CLAUDE.md

**Files:**

- Modify: `CLAUDE.md` (document simplified scope, remove notify_on_failure)

**Step 1: Read current service parameter section**

Run: `grep -n "notify_on_failure" CLAUDE.md` Expected: May show references in service
documentation

**Step 2: Add scope simplification note**

Edit `CLAUDE.md` in "Project Overview" section:

- Add after the first paragraph:

```markdown
**Scope**: Focused on core light control with verification/retry and preset management.
Notification feature and blueprints removed in v0.2.0.
```

**Step 3: Update service list if needed**

Edit `CLAUDE.md`:

- Verify "Adding New Service Parameters" section doesn't reference notify_on_failure
- If it does, remove those references

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document scope simplification in CLAUDE.md

Add note about removed features and simplified scope.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Run full test suite

**Files:**

- None (verification only)

**Step 1: Run all tests**

Run: `pytest tests/ -v` Expected: All tests pass (some tests removed, rest should pass)

**Step 2: Check test coverage**

Run:
`pytest tests/ --cov=custom_components/ha_light_controller --cov-report=term-missing`
Expected: Coverage >80%

**Step 3: Document results**

Note any failures or coverage issues. If failures occur, fix them before proceeding.

---

## Task 16: Update manifest version

**Files:**

- Modify: `custom_components/ha_light_controller/manifest.json:10`

**Step 1: Read current manifest**

Run: `grep version custom_components/ha_light_controller/manifest.json` Expected: Shows
`"version": "0.1.3"`

**Step 2: Update version to 0.2.0**

Edit `custom_components/ha_light_controller/manifest.json`:

- Change `"version": "0.1.3"` to `"version": "0.2.0"`

**Step 3: Commit**

```bash
git add custom_components/ha_light_controller/manifest.json
git commit -m "chore: bump version to 0.2.0

Version 0.2.0 marks scope simplification with removal of
notification feature and blueprints.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 17: Create CHANGELOG.md

**Files:**

- Create: `CHANGELOG.md`

**Step 1: Create changelog file**

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG.md for version tracking

Document v0.2.0 changes (removal of notifications and blueprints).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 18: Final verification and summary

**Files:**

- None (verification only)

**Step 1: Verify no notification references**

Run:
`grep -r "notify_on_failure\|NOTIFY_ON_FAILURE\|_send_notification" custom_components/ tests/ --exclude-dir=.git`
Expected: No output (or only unrelated test_notify_listener_exception)

**Step 2: Verify blueprints deleted**

Run: `find . -name "*.yaml" -path "*/blueprints/*"` Expected: No output

**Step 3: Verify all tests pass**

Run: `pytest tests/ -v` Expected: All tests pass

**Step 4: Create summary of changes**

Run: `git log --oneline | head -20` Expected: Shows all commits from this implementation

**Step 5: Count files changed**

Run: `git diff --stat main..HEAD` Expected: Shows summary of changes across all modified
files

---

## Success Criteria Checklist

After completing all tasks, verify:

- [ ] No references to `notify_on_failure` or `NOTIFY_ON_FAILURE` in codebase
- [ ] No `_send_notification()` method exists
- [ ] Blueprints directory deleted
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Test coverage >80% (`pytest --cov`)
- [ ] README.md updated (no notify_on_failure examples, no Blueprints section)
- [ ] USAGE.md updated (no Blueprints section)
- [ ] CLAUDE.md updated (documented scope change)
- [ ] Version bumped to 0.2.0 in manifest.json
- [ ] CHANGELOG.md created
- [ ] All changes committed with proper messages
- [ ] Working on `testing` branch (verify: `git branch --show-current`)

---

## Post-Implementation

After all tasks complete, the codebase will:

- Have notification feature completely removed from all 9 files
- Have blueprints directory deleted
- Have updated documentation reflecting simplified scope
- Have version 0.2.0 in manifest
- Have comprehensive changelog
- Maintain full test coverage and passing tests
- Be ready for PR to `testing` branch
