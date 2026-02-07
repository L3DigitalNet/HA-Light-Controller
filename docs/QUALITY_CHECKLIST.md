# Integration Quality Scale Checklist

Use this checklist to track your progress toward achieving [Home Assistant's Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) tiers.

## How to Use This Checklist

1. **Copy this checklist** to your integration's documentation
2. **Check off items** as you implement them
3. **Refer to linked resources** for implementation guidance
4. **Validate completion** by running quality checks before marking items complete

**Remember:** Higher tiers build on lower tiers. Achieve Bronze before targeting Silver, etc.

---

## Bronze Tier (Minimum Requirements)

Bronze tier is the **minimum acceptable quality** for custom integrations. All items must be completed.

###  Configuration & Setup

- [ ] **Config flow UI setup implemented** (`config_flow.py`)
  - No YAML configuration required
  - User can add integration via HA UI (Settings → Devices & Services)
  - See: [../custom_components/example_integration/config_flow.py](../custom_components/example_integration/config_flow.py)

- [ ] **`manifest.json` properly configured**
  - Required fields: domain, name, version, codeowners, documentation, issue_tracker
  - Correct `integration_type` (device, hub, service, virtual, helper)
  - Correct `iot_class` (local_polling, local_push, cloud_polling, cloud_push, calculated, assumed_state)
  - See: [../custom_components/example_integration/manifest.json](../custom_components/example_integration/manifest.json)

- [ ] **`async_setup_entry()` with automated tests**
  - Integration loads successfully from config entry
  - Test file exists: `tests/test_init.py`
  - Minimum one test validates setup
  - See: [../tests/test_init.py](../tests/test_init.py)

### Code Quality

- [ ] **Ruff linting passes (zero errors)**
  - Run: `ruff check custom_components/ --fix`
  - Run: `ruff format custom_components/`
  - All linting errors resolved
  - No `# noqa` comments without justification

- [ ] **Unique IDs for all entities**
  - Every entity has a stable `unique_id` property
  - IDs don't change between restarts
  - Format: `{DOMAIN}_{device_id}_{entity_type}`
  - See: [../custom_components/example_integration/entity.py](../custom_components/example_integration/entity.py)

- [ ] **At least one entity platform implemented**
  - Minimum one platform file (sensor.py, switch.py, etc.)
  - Entities properly registered and discoverable
  - Platform added to `PLATFORMS` in `__init__.py`

###  Documentation

- [ ] **Basic README.md with setup instructions**
  - How to install the integration
  - How to configure in HA UI
  - What entities are created
  - Basic troubleshooting

**Bronze Tier Complete?** ✅ All items above checked → You've achieved Bronze tier!

---

## Silver Tier (Reliability)

Silver tier focuses on **reliability and error handling**. Integrations should gracefully handle common failure scenarios.

### Error Handling

- [ ] **Connection errors raise `UpdateFailed`**
  - Coordinator's `_async_update_data()` catches `ConnectionError`
  - Raises `UpdateFailed` with descriptive message
  - Example: `raise UpdateFailed(f"Error communicating: {err}") from err`

- [ ] **Authentication failures raise `ConfigEntryAuthFailed`**
  - Invalid credentials trigger reauth flow
  - Import: `from homeassistant.exceptions import ConfigEntryAuthFailed`
  - Example: `raise ConfigEntryAuthFailed from err`

- [ ] **Entity availability properly managed**
  - Entities show as "unavailable" when device is offline
  - Availability restored when device comes back online
  - Uses CoordinatorEntity `available` property
  - See: [../custom_components/example_integration/entity.py](../custom_components/example_integration/entity.py)

- [ ] **Coordinator handles offline devices gracefully**
  - No exceptions bubble up to HA core
  - Appropriate error logging (not excessive)
  - Automatic reconnection attempts

### User Experience

- [ ] **Log-once patterns for repeated errors**
  - Use `_LOGGER.error()` once per error condition
  - Subsequent occurrences use `_LOGGER.debug()`
  - Prevents log flooding from persistent issues

- [ ] **Config flow error messages are user-friendly**
  - Errors shown in UI are clear and actionable
  - Error keys defined in `strings.json`
  - Examples: "cannot_connect", "invalid_auth", "unknown"

- [ ] **Troubleshooting documentation in README**
  - Common issues and solutions documented
  - Debug logging instructions provided
  - Contact/support information included

**Silver Tier Complete?** ✅ Bronze + all Silver items checked → You've achieved Silver tier!

---

## Gold Tier (Feature Complete)

Gold tier represents **feature-complete, production-quality** integrations.

### Code Quality

- [ ] **Full async codebase (no blocking I/O)**
  - All network requests use async libraries (aiohttp, asyncio)
  - No `requests`, `urllib`, or other sync libraries
  - File I/O uses `aiofiles` or `async_add_executor_job()`
  - See: [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)

- [ ] **Test coverage ≥ 90%**
  - Run: `pytest tests/ --cov=custom_components.your_integration --cov-report=term`
  - Coverage report shows ≥90% line coverage
  - All critical paths have tests
  - See: [../tests/](../tests/)

- [ ] **Complete type annotations (mypy strict passes)**
  - Run: `mypy custom_components/your_integration/`
  - Zero mypy errors in strict mode
  - All functions have return type hints
  - All parameters have type hints
  - See: [../mypy.ini](../mypy.ini)

### Efficiency

- [ ] **Efficient data handling (no redundant polls)**
  - Single coordinator manages data fetching
  - Entities read from coordinator data (no individual polling)
  - Update interval appropriate for device/service
  - See: [PERFORMANCE.md](PERFORMANCE.md)

- [ ] **Device registry integration**
  - Devices properly registered with HA device registry
  - `device_info` property implemented on entities
  - Devices show in UI with manufacturer/model
  - See: [../custom_components/example_integration/entity.py](../custom_components/example_integration/entity.py)

### Testing

- [ ] **All entity platforms have tests**
  - Every platform file (sensor.py, switch.py, etc.) has corresponding test file
  - Tests cover entity creation, state updates, and attributes
  - Tests use proper mocking (no real network calls)

- [ ] **Options flow for reconfiguration**
  - Users can reconfigure integration without deleting/re-adding
  - `async_step_init()` in config flow handles options
  - Options stored in `ConfigEntry.options`
  - Changes apply without reload when possible

**Gold Tier Complete?** ✅ Bronze + Silver + all Gold items checked → You've achieved Gold tier!

---

## Platinum Tier (Excellence)

Platinum tier represents **exceptional quality** suitable for Home Assistant core integrations.

### Code Excellence

- [ ] **Code follows all HA style guidelines**
  - Docstrings on all public classes/functions
  - Consistent naming conventions
  - No dead code or commented-out blocks
  - Follows [HA Code Review Guidelines](https://developers.home-assistant.io/docs/development_checklist)

- [ ] **Clear docstrings and comments**
  - Module-level docstrings explain purpose
  - Class docstrings describe responsibility
  - Function docstrings explain parameters and returns
  - Inline comments explain WHY, not WHAT

- [ ] **Performance optimized (minimal coordinator updates)**
  - Coordinator update interval justified
  - No unnecessary data fetching
  - Efficient data structures
  - Memory usage monitored and reasonable
  - See: [PERFORMANCE.md](PERFORMANCE.md)

### Maintenance & Support

- [ ] **Active maintenance plan documented**
  - CHANGELOG.md tracks all releases
  - Issues are triaged within 48 hours
  - Security issues have response plan
  - Deprecation notices provided 6+ months in advance

- [ ] **Security review completed**
  - No credentials logged
  - API keys stored securely
  - Input validation on all external data
  - HTTPS used for all network communication
  - See: [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)

- [ ] **Localization for multiple languages**
  - Strings extracted to `strings.json`
  - Translations provided for major languages
  - Dynamic strings use placeholders
  - See: [LOCALIZATION.md](LOCALIZATION.md)

- [ ] **Integration with HA diagnostics system**
  - `async_get_config_entry_diagnostics()` implemented
  - Diagnostic data helps troubleshooting
  - No sensitive data in diagnostics
  - See: [Home Assistant Diagnostics](https://developers.home-assistant.io/docs/integration_fetching_data#diagnostics)

**Platinum Tier Complete?** ✅ All tiers checked → You've achieved Platinum tier! 🎉

---

## Verification Commands

Use these commands to validate your implementation:

```bash
# Activate virtual environment
source venv/bin/activate

# Code quality checks
ruff check custom_components/ --fix
ruff format custom_components/
mypy custom_components/your_integration/

# Run tests with coverage
pytest tests/ --cov=custom_components.your_integration --cov-report=html -v

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Run all pre-commit hooks
pre-commit run --all-files
```

## Tier Progression Tips

### Bronze → Silver
**Focus on:** Error handling and user experience
- Add try/except blocks in coordinator
- Implement `ConfigEntryAuthFailed` for auth issues
- Test offline device scenarios
- Write clear error messages

### Silver → Gold
**Focus on:** Testing and efficiency
- Achieve 90% test coverage
- Ensure all code is async
- Add type hints everywhere
- Implement device registry
- Add options flow

### Gold → Platinum
**Focus on:** Polish and maintenance
- Add comprehensive docstrings
- Optimize performance
- Add localization
- Set up diagnostics
- Document maintenance plan

## Resources

- **Home Assistant Quality Scale**: https://developers.home-assistant.io/docs/core/integration-quality-scale/
- **Integration Checklist**: https://developers.home-assistant.io/docs/development_checklist
- **Testing**: https://developers.home-assistant.io/docs/development_testing
- **Coordinator Pattern**: https://developers.home-assistant.io/docs/integration_fetching_data

## Questions?

- Review [CLAUDE.md](../CLAUDE.md) for mandatory patterns
- Check [REFERENCE_GUIDE.md](../REFERENCE_GUIDE.md) for technical details
- See [example_integration/](../custom_components/example_integration/) for working code

---

**Remember:** Quality is a journey, not a destination. Start with Bronze and progressively enhance your integration over time. Each tier makes your integration more reliable and user-friendly.
