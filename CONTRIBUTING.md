# Contributing to HA-Light-Controller

Thank you for your interest in contributing! This document provides guidelines for contributing to the HA-Light-Controller custom integration.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Quality Standards](#quality-standards)
- [Code Style](#code-style)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

---

## Getting Started

This repository is a **Home Assistant custom integration for light control** with state verification, automatic retries, and preset management. Contributions should focus on:

1. **Improving light control features**
2. **Enhancing preset management**
3. **Fixing bugs and improving reliability**
4. **Updating documentation and guides**
5. **Adding tests and improving coverage**

### What NOT to Contribute

- Features outside the scope of light control and verification (e.g., other device types, notification systems)
- Major architectural changes without discussion
- Breaking changes without migration path
- Changes that violate Home Assistant async requirements

---

## Development Setup

### Prerequisites

- Python 3.14.2 or later (minimum 3.13)
- Git
- Home Assistant 2025.2.0+ (installed in venv)

### Quick Reference

Common development commands (see Makefile for all options):

```bash
make setup         # Initial setup (dependencies + pre-commit hooks)
make quality       # Run all quality checks
make test          # Run tests
make test-cov      # Run tests with coverage
make ci            # Simulate CI checks locally
make help          # Show all available commands
```

### Initial Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/L3DigitalNet/HA-Light-Controller.git
cd HA-Light-Controller

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# 3. Run initial setup (installs dependencies and pre-commit hooks)
make setup

# 4. Verify environment
make verify
```

**What `make setup` does:**
- Installs Home Assistant and all development dependencies (pytest, ruff, mypy, etc.)
- Configures pre-commit hooks for automatic code quality checks
- Prepares your environment for development

**Development Tools:**
- **Ruff** - Fast Python linter and formatter (replaces Black, isort, flake8)
- **mypy** - Static type checker with strict mode enabled
- **pytest** - Test framework with async support
- **pre-commit** - Automatic code quality checks before commits

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
make test-specific FILE=tests/test_config_flow.py

# View coverage report in browser
make coverage-report
```

**Alternative:** Direct pytest commands still work if needed:
```bash
pytest tests/ -v
pytest tests/ --cov=custom_components --cov-report=html
```

### Code Quality Checks

```bash
# Run all quality checks (lint, format, type-check, test)
make quality

# Individual checks:
make lint          # Run Ruff linter
make lint-fix      # Run Ruff linter with auto-fix
make format        # Format code with Ruff
make type-check    # Run mypy type checker
make pre-commit    # Run pre-commit hooks

# Simulate CI checks locally
make ci
```

**Alternative:** Direct tool commands still work:
```bash
ruff check custom_components/ tests/ scripts/ --fix
ruff format custom_components/ tests/ scripts/
mypy custom_components/
pre-commit run --all-files
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:

```
docs/add-security-guide
feat/oauth2-example
fix/coordinator-error-handling
chore/update-dependencies
```

### Commit Messages

Follow conventional commit format:

```
feat: add OAuth2 example integration
fix: correct coordinator error handling
docs: update HACS integration guide
test: add config flow tests
chore: update pre-commit hooks
```

**Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `test` - Adding or updating tests
- `chore` - Maintenance tasks
- `refactor` - Code refactoring
- `style` - Code style changes (formatting)

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make your changes**
   - Write code
   - Add/update tests
   - Update documentation

3. **Test your changes**
   ```bash
   make quality  # Runs all quality checks
   # or individually:
   make test
   make lint-fix
   make type-check
   ```

4. **Update CHANGELOG.md**
   ```markdown
   ## [Unreleased]
   ### Added
   - New OAuth2 example integration
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add OAuth2 example integration"
   ```

6. **Push to your fork**
   ```bash
   git push origin feat/your-feature
   ```

7. **Open a Pull Request**

---

## Pull Request Process

### Before Submitting

- [ ] All tests pass (`make test` or `pytest tests/`)
- [ ] Code passes linting (`make lint-fix` or `ruff check . --fix`)
- [ ] Code is formatted (`make format` or `ruff format .`)
- [ ] Type checking passes (`make type-check` or `mypy custom_components/`)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated (if applicable)
- [ ] Pre-commit hooks pass (`make pre-commit` or `pre-commit run --all-files`)

**Quick check:** Run `make ci` to simulate all CI checks locally.

### PR Title

Use conventional commit format:

```
feat: add OAuth2 authentication example
fix: correct coordinator timeout handling
docs: improve HACS integration guide
```

### PR Description

Use the provided template and include:

1. **What changed** - Brief description
2. **Why it changed** - Motivation and context
3. **Testing** - How you tested the changes
4. **Checklist** - Complete all items

### Review Process

1. **Automated checks** run on every PR
2. **Maintainer review** typically within 7 days
3. **Address feedback** by pushing new commits
4. **Approval** required before merge
5. **Squash and merge** for clean history

---

## Quality Standards

All code must meet these standards:

### Code Quality

- **Ruff linting**: Zero errors
- **Type hints**: All functions have return type hints
- **Docstrings**: All public functions documented
- **Mypy**: Passes in strict mode

### Test Coverage

- **Minimum 80% coverage** for new code
- **All new features** have tests
- **Bug fixes** include regression tests
- **Integration tests** for config flows

### Documentation

- **New features** documented in relevant guides
- **Code comments** explain WHY, not WHAT
- **README** updated for user-facing changes
- **CHANGELOG** updated for all changes

---

## Code Style

### Python

Follow PEP 8 and Home Assistant's style guidelines:

```python
"""Module docstring."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# Constants
DEFAULT_TIMEOUT: Final[int] = 30

class MyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator description.

    Longer explanation of what this coordinator does.
    """

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize coordinator.

        Args:
            hass: Home Assistant instance.
            host: Device hostname or IP.
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self._host = host

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device.

        Returns:
            Device data dictionary.

        Raises:
            UpdateFailed: When device is unreachable.
        """
        try:
            return await self._fetch_data()
        except ConnectionError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err
```

### Type Hints

Use modern Python 3.14+ syntax:

```python
# ✅ CORRECT
from typing import Any

def process_data(data: dict[str, Any]) -> list[str]:
    """Process data."""
    items: list[str] = []
    return items

# ❌ WRONG (old syntax)
from typing import Dict, List, Any

def process_data(data: Dict[str, Any]) -> List[str]:
    """Process data."""
    items: List[str] = []
    return items
```

### Imports

Order imports as:

1. Future imports (`from __future__ import annotations`)
2. Standard library
3. Third-party libraries
4. Home Assistant core
5. Local imports

```python
from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
```

---

## Testing Requirements

### Test Structure

```python
"""Test the example integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

from custom_components.example_integration import async_setup_entry


async def test_setup_entry(hass, mock_api):
    """Test successful setup."""
    entry = ConfigEntry(
        version=1,
        domain="example_integration",
        title="Test Device",
        data={CONF_HOST: "192.168.1.100"},
        source="user",
    )

    assert await async_setup_entry(hass, entry)
    await hass.async_block_till_done()

    # Verify setup
    assert hass.data["example_integration"][entry.entry_id] is not None
```

### Mocking

Use pytest fixtures for mocking:

```python
@pytest.fixture
def mock_api():
    """Mock API client."""
    with patch("custom_components.example_integration.APIClient") as mock:
        mock.return_value.fetch_data.return_value = {"value": 42}
        yield mock
```

### Test Coverage

Check coverage after adding tests:

```bash
# Run tests with coverage report
make test-cov

# Open HTML coverage report in browser
make coverage-report
```

**Alternative:** Direct pytest commands:
```bash
pytest tests/ --cov=custom_components --cov-report=html
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

---

## Documentation

### Documentation Standards

- **Clear and concise** - Get to the point
- **Code examples** - Show, don't just tell
- **Why, not just what** - Explain rationale
- **User-focused** - Write for developers using the template

### Updating Guides

When adding features, update relevant documentation:

- `README.md` - User-facing changes
- `CLAUDE.md` - AI assistant instructions
- `docs/` guides - Implementation patterns
- `CHANGELOG.md` - All changes
- Code comments - Complex logic

### Writing Examples

Provide complete, runnable examples:

```python
# ✅ GOOD - Complete example
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class ExampleCoordinator(DataUpdateCoordinator):
    """Example coordinator."""

    async def _async_update_data(self):
        """Fetch data."""
        return await self.api.fetch_data()

# ❌ BAD - Incomplete snippet
async def _async_update_data(self):
    return await self.api.fetch_data()
```

---

## Getting Help

### Questions?

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - General questions, ideas
- **Home Assistant Community** - Integration development help

### Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.

---

**Thank you for contributing!** Your efforts help developers worldwide create better Home Assistant integrations.
