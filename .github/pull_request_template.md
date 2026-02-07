# Description

Please include a summary of the changes and the related issue. Include relevant motivation and context.

Fixes # (issue)

## Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement (refactoring, type hints, tests)

## Integration Quality Scale

Which quality tier does this PR target or improve? See [docs/QUALITY_CHECKLIST.md](../docs/QUALITY_CHECKLIST.md) for detailed requirements.

- [ ] Bronze (Config flow, basic tests, manifest)
- [ ] Silver (Error handling, availability, documentation)
- [ ] Gold (Full async, type coverage, comprehensive tests)
- [ ] Platinum (Best practices, performance, maintenance)

## How Has This Been Tested?

Please describe the tests that you ran to verify your changes.

- [ ] Test A (e.g., pytest tests/test_config_flow.py)
- [ ] Test B (e.g., manual testing with actual device)

**Test Configuration**:
- Home Assistant version:
- Python version:
- Integration version:

## Checklist

Please ensure all items are checked before submitting:

### Code Quality
- [ ] My code follows the style guidelines of this project (Ruff passes)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added type hints to new functions/methods
- [ ] Type checking passes (mypy custom_components/)

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage has not decreased

### Async Requirements
- [ ] All I/O operations are async (no blocking calls)
- [ ] I have used aiohttp instead of requests
- [ ] I have used `async_add_executor_job` for unavoidable sync operations

### DataUpdateCoordinator (if applicable)
- [ ] I am using DataUpdateCoordinator for polling data
- [ ] I have implemented proper error handling (UpdateFailed, ConfigEntryAuthFailed)
- [ ] I have set an appropriate update_interval

### Entities (if applicable)
- [ ] All entities have unique IDs
- [ ] All entities implement proper availability handling
- [ ] Entities are grouped by device (DeviceInfo)
- [ ] Entity names follow HA conventions (_attr_has_entity_name = True)

### Config Flow (if applicable)
- [ ] Config flow is implemented (no YAML configuration)
- [ ] Config flow has error handling
- [ ] Config flow prevents duplicate entries (unique_id)
- [ ] strings.json includes all UI text

### Documentation
- [ ] **I have updated CHANGELOG.md with this change** (Required for all non-trivial changes)
- [ ] I have updated the README.md (if needed)
- [ ] I have added docstrings to new functions/classes
- [ ] I have updated manifest.json version (if releasing)

### Pre-commit Hooks
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`

## Screenshots / Logs (if applicable)

Add screenshots or relevant log output to help explain your changes.

```
Paste logs here if applicable
```

## Additional Notes

Add any other notes about the PR here.

## Review Checklist for Maintainers

- [ ] Code follows HA integration best practices
- [ ] Meets or improves Integration Quality Scale tier
- [ ] All CI checks pass
- [ ] Breaking changes are documented
- [ ] Version number updated (if applicable)
