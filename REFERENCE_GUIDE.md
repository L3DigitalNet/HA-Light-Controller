# HA-Light-Controller - Complete Reference Guide

**Version:** 0.2.1 **Date:** February 7, 2026 **Python Version:** 3.14.2 (minimum 3.13)
| Home Assistant 2025.2.0+

This comprehensive guide documents the complete setup and usage of the
HA-Light-Controller Home Assistant custom integration, including AI agents, automation,
and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [AI Agent System](#ai-agent-system)
4. [Automation Infrastructure](#automation-infrastructure)
5. [Development Workflows](#development-workflows)
6. [Quality Standards](#quality-standards)
7. [Quick Reference](#quick-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What HA-Light-Controller Provides

HA-Light-Controller is a production-ready Home Assistant custom integration providing:

- ✅ **Reliable Light Control** - State verification with automatic retries
- ✅ **Preset Management** - Save and activate lighting scenes programmatically
- ✅ **Service-Based API** - Control via services and YAML automation
- ✅ **Entity Platform** - Buttons and sensors for preset activation
- ✅ **AI Agent Assistance** - Specialized agents for Claude Code, Copilot, Codex
- ✅ **Automated Quality Enforcement** - CI/CD, pre-commit hooks, VS Code tasks
- ✅ **Testing Framework** - pytest with HA custom component support
- ✅ **Code Quality Tools** - Ruff, mypy, pre-commit
- ✅ **Comprehensive Documentation** - Guides, patterns, troubleshooting

### Key Features

| Feature                | Description                                     | Status   |
| ---------------------- | ----------------------------------------------- | -------- |
| **Python Environment** | Python 3.14.2 (minimum 3.13)                    | ✅ Ready |
| **Home Assistant**     | Custom integration with config flow (2025.2.0+) | ✅ Ready |
| **Light Control**      | ensure_state service with verification/retry    | ✅ Ready |
| **Preset System**      | Create, activate, manage presets via UI/service | ✅ Ready |
| **Testing**            | pytest + mocked HA environment                  | ✅ Ready |
| **Linting**            | Ruff (official HA standard)                     | ✅ Ready |
| **Type Checking**      | mypy with strict mode                           | ✅ Ready |
| **Pre-commit**         | Git hooks for quality gates                     | ✅ Ready |
| **CI/CD**              | GitHub Actions pipeline                         | ✅ Ready |
| **AI Agents**          | Claude, Copilot, Codex integration              | ✅ Ready |
| **VS Code Tasks**      | Interactive development tasks                   | ✅ Ready |
| **Makefile**           | Comprehensive development commands              | ✅ Ready |
| **Documentation**      | Complete guides and examples                    | ✅ Ready |

---

## Project Structure

### Directory Layout

```
HA-Light-Controller/
├── .github/                              # GitHub configuration
│   ├── workflows/
│   │   └── ci.yml                        # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml                # Bug report form
│   │   ├── feature_request.yml           # Feature request form
│   │   └── config.yml                    # Template config
│   ├── pull_request_template.md          # PR checklist
│   ├── dependabot.yml                    # Dependency updates
│   ├── copilot-instructions.md           # GitHub Copilot context
│   └── AUTOMATION_GUIDE.md               # Automation documentation
│
├── .vscode/                              # VS Code configuration
│   ├── settings.json                     # Editor settings
│   ├── tasks.json                        # Development tasks
│   └── codex-instructions.md             # Codex context
│
├── custom_components/                    # HA integrations
│   └── ha_light_controller/              # Main integration
│       ├── __init__.py                   # Entry point, service registration
│       ├── manifest.json                 # Integration metadata
│       ├── config_flow.py                # Config flow (UI setup)
│       ├── const.py                      # Constants
│       ├── controller.py                 # Light control logic
│       ├── preset_manager.py             # Preset CRUD operations
│       ├── button.py                     # Preset activation buttons
│       ├── sensor.py                     # Preset status sensors
│       ├── services.yaml                 # Service definitions
│       ├── strings.json                  # UI strings
│       └── translations/
│           └── en.json                   # English translations
│
├── tests/                                # Test suite
│   ├── conftest.py                       # Shared fixtures
│   ├── test_controller.py                # Controller tests
│   ├── test_preset_manager.py            # Preset manager tests
│   ├── test_config_flow.py               # Config flow tests
│   └── README.md                         # Testing guide
│
├── scripts/                              # Utility scripts
│   └── verify_environment.py             # Environment verification
│
├── resources/                            # Development resources
│   └── agents/
│       └── ha-integration-agent/         # HA development agent
│           ├── README.md                 # Installation & usage guide
│           ├── ha_integration_agent_system_prompt.md  # Agent definition
│           ├── ha_integration_agent_spec.md           # Comprehensive patterns
│           └── [example files]           # Reference implementations
│
├── CLAUDE.md                             # Project instructions for Claude
├── README.md                             # Project overview
├── REFERENCE_GUIDE.md                    # This file
├── pyproject.toml                        # Project configuration
├── .pre-commit-config.yaml               # Pre-commit hooks
└── .gitignore                            # Git ignore rules
```

### Key Files Explained

#### Configuration Files

| File                      | Purpose                      | When to Edit               |
| ------------------------- | ---------------------------- | -------------------------- |
| `pyproject.toml`          | Ruff, mypy, pytest config    | Rarely - already optimized |
| `.pre-commit-config.yaml` | Git hook configuration       | When adding new hooks      |
| `.vscode/settings.json`   | VS Code editor settings      | Personal preference        |
| `CLAUDE.md`               | Instructions for Claude Code | When patterns change       |

#### Documentation Files

| File                          | Purpose                        | Audience       |
| ----------------------------- | ------------------------------ | -------------- |
| `README.md`                   | Project overview               | All developers |
| `CLAUDE.md`                   | Claude Code instructions       | AI assistant   |
| `REFERENCE_GUIDE.md`          | Complete reference (this file) | All developers |
| `.github/AUTOMATION_GUIDE.md` | Automation details             | Maintainers    |

#### Automation Files

| File                       | Purpose            | Tool           |
| -------------------------- | ------------------ | -------------- |
| `.github/workflows/ci.yml` | CI/CD pipeline     | GitHub Actions |
| `.vscode/tasks.json`       | Interactive tasks  | VS Code        |
| `.pre-commit-config.yaml`  | Git hooks          | Pre-commit     |
| `.github/dependabot.yml`   | Dependency updates | Dependabot     |

---

## AI Agent System

### Overview

HA-Light-Controller includes specialized AI agents to assist with Home Assistant
integration development.

### Installed Agents

#### 1. HA Integration Agent (Claude Code)

**Location:** `~/.claude/agents/ha-integration-agent.md`

**Capabilities:**

- Generates complete integration structure
- Creates DataUpdateCoordinator implementations
- Builds config flows with all steps
- Generates entity platform files
- Writes test files with proper mocking
- Reviews code against Quality Scale
- Provides architecture guidance

**How to Use:**

```python
# Method 1: Task tool
Task(
    subagent_type="ha-integration-agent",
    prompt="Help me implement retry logic for light control",
    description="Add retry logic to controller"
)

# Method 2: Chat interface
@agent ha-integration-agent
I need to modify the preset manager to support...
```

**When to Use:**

- Adding new features (service parameters, entity types)
- Implementing patterns (async operations, error handling)
- Code review (Quality Scale compliance)
- Debugging (understanding errors)
- Learning (understanding WHY patterns exist)

#### 2. GitHub Copilot Integration

**Location:** `.github/copilot-instructions.md`

**Auto-Detection:** GitHub Copilot automatically reads this file

**What It Does:**

- Suggests async-first code patterns
- Generates proper config flows
- Follows HA type hint conventions
- Implements error handling
- Creates unique IDs for entities

**How to Use:**

```python
# Just start typing, Copilot suggests HA-compliant code
async def _expand_entity(self, entity_id: str) -> list[str]:
    # Press Tab - Copilot suggests implementation
```

#### 3. VS Code Codex Integration

**Location:** `.vscode/codex-instructions.md`

**How to Use:**

```python
# Add comment referencing pattern
# Generate async light control following HA Quality Scale Bronze tier
async def ensure_state(self, ...):
    # Codex generates based on context
```

### Agent Documentation

#### Complete Installation Guide

**File:** `resources/agents/ha-integration-agent/README.md` (655 lines)

**Contents:**

- Installation instructions for all 3 platforms
- Usage examples with code
- Agent capabilities reference
- Code patterns (async operations, config flow, entities)
- Quality Scale requirements
- Common pitfalls
- Testing requirements
- Troubleshooting
- Best practices

#### Comprehensive Specification

**File:** `resources/agents/ha-integration-agent/ha_integration_agent_spec.md` (750
lines)

**Contents:**

- Executive summary
- Core knowledge base (Python versions, Quality Scale)
- Critical development patterns
- Complete manifest.json reference
- Testing requirements
- Common pitfalls and solutions
- Development environment setup
- Agent workflow phases
- Community resources

#### Agent System Prompt

**File:** `resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md`
(190 lines)

**Contents:**

- Agent core identity
- Structured workflow (Discovery → Implementation → Quality)
- Technical requirements enforcement
- Communication style guidelines
- Common Q&A

---

## Automation Infrastructure

### Four Automation Layers

This integration provides **four complementary automation systems**:

```
┌─────────────────────────────────────────┐
│ 1. GitHub Actions (CI/CD)              │
│    Runs on: push, PR                    │
│    Enforces: Bronze tier minimum        │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│ 2. Pre-commit Hooks                     │
│    Runs on: git commit                  │
│    Catches: Style, type, format issues  │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│ 3. VS Code Tasks                        │
│    Runs on: Ctrl+Shift+B (manual)       │
│    Provides: Interactive feedback       │
└─────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────┐
│ 4. Command-Line Interface               │
│    Runs on: pytest, ruff, mypy commands │
│    Provides: Direct tool access         │
└─────────────────────────────────────────┘
```

### 1. GitHub Actions CI/CD

**File:** `.github/workflows/ci.yml`

**Triggers:**

- Push to `main` or `testing` branches
- Pull requests to `main` or `testing`
- Manual workflow dispatch

**Jobs:**

| Job            | Command                              | Duration | Required |
| -------------- | ------------------------------------ | -------- | -------- |
| **Lint**       | `ruff check` + `ruff format --check` | ~30s     | ✅       |
| **Type Check** | `mypy custom_components/`            | ~45s     | ✅       |
| **Test**       | `pytest tests/` (Python 3.14)        | ~2min    | ✅       |
| **All Checks** | Gate job (all must pass)             | ~1s      | ✅       |

**Features:**

- Pip dependency caching
- Coverage report generation
- Codecov upload (optional)
- Detailed error reporting

**Setup Codecov (Optional):**

1. Sign up: https://codecov.io/
2. Add repository
3. Get token
4. Add GitHub secret: `CODECOV_TOKEN`

### 2. VS Code Tasks

**File:** `.vscode/tasks.json`

**Quick Access:** Press `Ctrl+Shift+B` (Linux/Windows) or `Cmd+Shift+B` (Mac)

**Available Tasks:**

| Task                    | Shortcut       | Description                             |
| ----------------------- | -------------- | --------------------------------------- |
| **Quality Check (All)** | `Ctrl+Shift+B` | Default: lint, format, type-check, test |
| Run All Tests           | Task menu      | pytest tests/ -v                        |
| Run Tests with Coverage | Task menu      | pytest with HTML report                 |
| Lint with Ruff          | Task menu      | Check code for issues                   |
| Lint and Fix with Ruff  | Task menu      | Auto-fix linting issues                 |
| Format with Ruff        | Task menu      | Format code                             |
| Type Check with mypy    | Task menu      | Check type hints                        |
| Run Pre-commit Hooks    | Task menu      | Run all hooks                           |
| Open Coverage Report    | Task menu      | Open htmlcov/index.html                 |

**How to Use:**

1. Press `Ctrl+Shift+P` → "Tasks: Run Task"
2. Or press `Ctrl+Shift+B` for default build
3. Or Terminal menu → "Run Task..."

**Problem Matchers:**

- Ruff errors show inline
- mypy errors show inline
- pytest failures show in Problems panel

### 3. Command-Line Interface

**Quick Reference:**

```bash
# Quality Checks
pytest tests/                          # Run all tests
pytest tests/ --cov=custom_components  # Tests with coverage
ruff check custom_components/          # Lint only (check)
ruff check --fix custom_components/    # Lint with auto-fix
ruff format custom_components/         # Format code
mypy custom_components/                # Type check
pre-commit run --all-files             # Run pre-commit hooks

# Testing
pytest tests/ -v                       # Verbose test output
pytest tests/test_controller.py        # Run specific file
pytest tests/test_controller.py::test_ensure_state_single_light  # Specific test
pytest tests/ --cov=custom_components --cov-report=html  # HTML coverage report
xdg-open htmlcov/index.html            # Open coverage report

# Development
pytest --lf                            # Re-run last failed tests
pytest -k "test_preset"                # Run tests matching pattern
```

**Examples:**

```bash
# Run all quality checks
ruff check --fix custom_components/
ruff format custom_components/
mypy custom_components/
pytest tests/

# Run tests with coverage
pytest tests/ --cov=custom_components --cov-report=html
xdg-open htmlcov/index.html

# Run specific test file
pytest tests/test_controller.py -v

# Development mode - watch for changes
# Requires: sudo apt install entr
find custom_components tests -name "*.py" | entr -c pytest tests/
```

### 4. Pre-commit Hooks

**File:** `.pre-commit-config.yaml`

**Runs Automatically:** On every `git commit`

**Installed Hooks:**

| Hook                    | Purpose                 | Auto-Fix |
| ----------------------- | ----------------------- | -------- |
| trailing-whitespace     | Remove trailing spaces  | ✅       |
| end-of-file-fixer       | Ensure newline at EOF   | ✅       |
| check-yaml              | Validate YAML syntax    | ❌       |
| check-added-large-files | Prevent files >500KB    | ❌       |
| check-merge-conflict    | Detect conflict markers | ❌       |
| ruff                    | Lint Python code        | ✅       |
| ruff-format             | Format Python code      | ✅       |
| mypy                    | Type check Python code  | ❌       |

**Manual Execution:**

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files custom_components/ha_light_controller/*.py

# Run specific hook
pre-commit run ruff --all-files

# Update hook versions
pre-commit autoupdate

# Reinstall hooks
pre-commit clean
pre-commit install
```

**Skip Hooks (Emergency Only):**

```bash
# NOT RECOMMENDED
git commit --no-verify -m "Emergency fix"

# Better: Fix the issues
pre-commit run --all-files
git add .
git commit -m "Fixed issues"
```

### 5. Dependabot

**File:** `.github/dependabot.yml`

**Schedule:** Weekly on Mondays at 9:00 AM

**Monitors:**

- Python packages (pip)
- GitHub Actions versions

**Dependency Groups:**

| Group              | Packages                                                                  |
| ------------------ | ------------------------------------------------------------------------- |
| **Home Assistant** | homeassistant, aiohttp, voluptuous                                        |
| **Testing**        | pytest, pytest-asyncio, pytest-homeassistant-custom-component, pytest-cov |
| **Code Quality**   | ruff, mypy, pre-commit                                                    |

**Configuration:**

- Max 10 open PRs for pip
- Max 5 open PRs for GitHub Actions
- Auto-labels: `dependencies`, `python`, `github-actions`
- Commit prefix: `deps:` or `ci:`

**⚠️ Action Required:** Edit `.github/dependabot.yml` and replace `your-github-username`
with your actual GitHub username in the `reviewers` and `assignees` fields.

### 6. Issue & PR Templates

#### Bug Report Template

**File:** `.github/ISSUE_TEMPLATE/bug_report.yml`

**Collects:**

- Bug description
- Steps to reproduce
- Expected behavior
- Log output
- HA version, integration version, Python version
- Configuration (sanitized)
- Additional context

#### Feature Request Template

**File:** `.github/ISSUE_TEMPLATE/feature_request.yml`

**Collects:**

- Problem description
- Proposed solution
- Alternatives considered
- Affected components
- Willingness to contribute
- Additional context

#### PR Template

**File:** `.github/pull_request_template.md`

**Sections:**

- Description & issue reference
- Type of change
- Quality tier target
- Testing verification
- Comprehensive checklist
- Screenshots/logs
- Additional notes

**Checklist Categories:**

- Code Quality
- Testing
- Async Requirements
- Documentation
- Pre-commit Hooks

---

## Development Workflows

### Initial Setup

```bash
# 1. Navigate to project
cd /home/chris/projects/HA-Light-Controller

# 2. Complete setup (installs dependencies + pre-commit hooks)
make setup

# 3. Verify setup
make verify

# 4. Run quality checks
make quality
```

**Alternative (manual setup):**

```bash
# 1. Activate virtual environment (if using one)
source venv/bin/activate  # If you have a venv

# 2. Install dependencies
pip install -U pip
pip install homeassistant aiohttp voluptuous
pip install pytest pytest-asyncio pytest-homeassistant-custom-component pytest-cov
pip install ruff mypy pre-commit

# 3. Install pre-commit hooks
pre-commit install

# 4. Verify setup
pytest tests/
ruff check custom_components/
mypy custom_components/
```

### Development Cycle

#### Standard Workflow

```bash
# 1. Edit code
# Edit custom_components/ha_light_controller/...

# 2. Run quality checks
make quality            # Runs: lint-fix, format, type-check, test

# 3. Check coverage
make test-cov           # Generates HTML coverage report
make coverage-report    # Opens report in browser

# 4. Commit (pre-commit hooks run automatically)
git add .
git commit -m "Add feature X"

# 5. Push (CI runs automatically)
git push
```

**Alternative (manual commands):**

```bash
# 2. Run quality checks manually
ruff check --fix custom_components/
ruff format custom_components/
mypy custom_components/
pytest tests/

# 3. Check coverage manually
pytest tests/ --cov=custom_components --cov-report=html
xdg-open htmlcov/index.html
```

#### Watch Mode (Development)

```bash
# Auto-run tests on file changes (requires entr)
make watch-test

# Or manually:
find custom_components tests -name "*.py" | entr -c pytest tests/ -v

# In another terminal, edit code
# Tests run automatically when you save
```

### Testing Workflows

#### Run All Tests

```bash
# Option 1: Makefile (recommended)
make test

# Option 2: Direct pytest
pytest tests/ -v

# Option 3: VS Code Task
# Ctrl+Shift+P → Tasks: Run Task → Run All Tests
```

#### Run with Coverage

```bash
# Option 1: Makefile (recommended)
make test-cov           # Generate HTML report
make coverage-report    # Open report in browser

# Option 2: Direct pytest
pytest tests/ --cov=custom_components --cov-report=html
xdg-open htmlcov/index.html
```

#### Run Specific Tests

```bash
# Option 1: Makefile
make test-specific FILE=tests/test_config_flow.py

# Option 2: Direct pytest
pytest tests/test_config_flow.py -v                      # Specific file
pytest tests/test_config_flow.py::test_user_flow -v     # Specific test function
pytest tests/ -k "test_preset" -v                       # Tests matching pattern
```

### Testing Best Practices

#### ✅ DO: Module-Level Imports

Import integration code at the module level, not inside test functions:

```python
# ✅ CORRECT - Module level
from custom_components.ha_light_controller import PLATFORMS, async_setup_entry

async def test_setup():
    assert async_setup_entry is not None

# ❌ WRONG - Inside function
async def test_setup():
    from custom_components.ha_light_controller import async_setup_entry  # Don't!
    assert async_setup_entry is not None
```

**Why:** Pytest imports test modules during collection, before fixtures run.
Module-level imports work correctly, but imports inside functions can fail with path
resolution issues.

#### ✅ DO: Clear Caches When Type Checking Fails

```bash
# Mypy giving weird errors? Clear cache!
rm -rf .mypy_cache
mypy custom_components/

# Pre-commit mypy acting different? Rebuild environment
pre-commit clean
pre-commit install
```

**Why:** Mypy caches type information for performance. Stale caches cause confusing,
inconsistent errors.

#### ✅ DO: Test Both Ways

```bash
# Test with manual commands
mypy custom_components/
pytest tests/ -v

# Test with pre-commit (what CI uses)
pre-commit run --all-files
```

**Why:** Pre-commit and CI run in isolated environments that can behave differently than
your local setup.

#### ✅ DO: Ensure Package Structure

```bash
# Required files for proper Python imports
custom_components/__init__.py              # Makes it a package
custom_components/ha_light_controller/     # The integration
tests/conftest.py                          # Adds path to sys.path
```

**Why:** Without `__init__.py`, Python won't treat custom_components as a package,
causing import errors.

#### ❌ DON'T: Override Tool Configs in Pre-commit

```yaml
# ❌ BAD - Overrides mypy.ini
- id: mypy
  args: [--strict, --ignore-missing-imports]

# ✅ GOOD - Uses mypy.ini
- id: mypy
  additional_dependencies:
    - homeassistant
```

**Why:** Command-line args override config files, causing inconsistent behavior between
manual runs and pre-commit.

### Quality Check Workflows

#### Before Committing

```bash
# Option 1: Makefile (recommended)
make quality            # Runs all checks: lint-fix, format, type-check, test

# Option 2: Manual commands
ruff check --fix custom_components/
ruff format custom_components/
mypy custom_components/
pytest tests/
```

#### Before Creating PR

```bash
# Option 1: Makefile (simulates CI environment)
make ci                 # Runs all checks exactly as CI does

# Option 2: Manual commands (in order)
ruff check custom_components/
ruff format --check custom_components/
mypy custom_components/
pytest tests/ -v

# Should all pass before creating PR
```

#### Continuous Checks (VS Code)

```bash
# Set up format-on-save
# .vscode/settings.json already configured

# Run checks manually
# Ctrl+Shift+B → Quality Check (All)
```

### Git Workflow

#### Standard Flow

```bash
# 1. Create feature branch
git checkout -b feature/new-parameter

# 2. Make changes
# ... edit files ...

# 3. Run quality checks
make quality            # Or: make ci to simulate CI environment

# 4. Commit (hooks run automatically)
git add .
git commit -m "Add new service parameter"

# 5. Push
git push origin feature/new-parameter

# 6. Create PR on GitHub
# CI runs automatically
```

#### Pre-commit Hooks

Hooks run automatically on commit:

- Remove trailing whitespace
- Fix end-of-file
- Validate YAML
- Lint with Ruff
- Format with Ruff
- Type check with mypy

**If hooks fail:**

```bash
# Hooks auto-fix what they can
# Review changes
git add .

# Commit again
git commit -m "Add new service parameter"
```

---

## Quality Standards

### Integration Quality Scale

#### Bronze Tier (Minimum Required)

**Requirements:**

- ✅ Config flow UI setup
- ✅ Automated setup tests
- ✅ Basic coding standards (Ruff passes)
- ✅ Proper manifest.json

**How to Achieve:**

```bash
# Must pass these checks
ruff check custom_components/           # Ruff must pass
pytest tests/                           # Basic tests must pass
mypy custom_components/                 # No critical type errors
```

**Example:**

```python
# Config flow required
class LightControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    # Implementation...

# Tests required
async def test_form(hass):
    result = await hass.config_entries.flow.async_init(DOMAIN, ...)
    assert result["type"] == "form"
```

#### Silver Tier (Reliability)

**Requirements:**

- ✅ All Bronze requirements
- ✅ Proper error handling (auth failures, offline devices)
- ✅ Entity availability management
- ✅ Troubleshooting documentation
- ✅ Log-once patterns for connection issues

**How to Achieve:**

```python
# Proper error handling in services
async def async_handle_ensure_state(call: ServiceCall) -> ServiceResponse:
    try:
        result = await controller.ensure_state(...)
        return result.to_dict()
    except Exception as err:
        _LOGGER.error("Failed to ensure light state: %s", err)
        raise HomeAssistantError(f"Failed to control lights: {err}") from err

# Availability handling in entities
@property
def available(self) -> bool:
    return self._preset_manager.get_preset(self._preset_id) is not None
```

#### Gold Tier (Feature Complete)

**Requirements:**

- ✅ All Silver requirements
- ✅ Full async codebase (no blocking operations)
- ✅ Comprehensive test coverage (>80%)
- ✅ Complete type annotations (mypy strict passes)
- ✅ Efficient data handling

**How to Achieve:**

```bash
# Must pass these checks
mypy custom_components/                 # mypy must pass with 0 errors
pytest tests/ --cov=custom_components   # Coverage >80%

# All I/O must be async
# Use aiohttp, not requests
# Use async libraries for all operations
```

#### Platinum Tier (Excellence)

**Requirements:**

- ✅ All Gold requirements
- ✅ All coding standards and best practices
- ✅ Clear code comments and documentation
- ✅ Optimal performance
- ✅ Active code ownership and maintenance

**How to Achieve:**

- Document all complex logic
- Optimize performance (minimal API calls)
- Respond to issues promptly
- Keep dependencies updated

### Mandatory Patterns

#### 1. Config Flow (REQUIRED for All New Integrations)

```python
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title="HA Light Controller",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({...}),
            errors=errors,
        )
```

**Why:** Provides consistent UI experience, required for Bronze tier, mandatory for core
integrations.

#### 2. Async-First Architecture (REQUIRED)

```python
# ✅ CORRECT - Async library
import aiohttp

async def fetch_data(self, url: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ❌ WRONG - Blocks event loop
import requests

async def fetch_data(self, url: str) -> dict[str, Any]:
    return requests.get(url).json()  # BLOCKS ENTIRE HA!

# ✅ ACCEPTABLE - If no async library exists
async def fetch_data(self, url: str) -> dict[str, Any]:
    return await self.hass.async_add_executor_job(
        requests.get, url
    )
```

**Why:** Home Assistant is async. Blocking operations freeze the entire system.

#### 3. Full Type Hints (REQUIRED)

```python
from __future__ import annotations

from typing import Any, Final

# ✅ CORRECT - Modern syntax
DOMAIN: Final = "ha_light_controller"
DEFAULT_TIMEOUT: Final[int] = 30

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up from config entry."""
    data: dict[str, Any] = entry.data
    devices: list[str] = data.get("devices", [])

# ❌ WRONG - Old syntax
from typing import List, Dict

devices: List[str] = []  # Use list[str]
data: Dict[str, Any] = {}  # Use dict[str, Any]
```

**Why:** Type safety, IDE support, Gold tier requirement, modern Python standard.

#### 4. Service Registration Pattern

```python
# Services registered via loop with lambda capture for cleanup
services = [
    (SERVICE_ENSURE_STATE, async_handle_ensure_state, SERVICE_ENSURE_STATE_SCHEMA),
    (SERVICE_ACTIVATE_PRESET, async_handle_activate_preset, SERVICE_ACTIVATE_PRESET_SCHEMA),
    # ...
]

for service_name, handler, schema in services:
    hass.services.async_register(
        DOMAIN, service_name, handler,
        schema=schema, supports_response=SupportsResponse.OPTIONAL
    )
    entry.async_on_unload(lambda svc=service_name: hass.services.async_remove(DOMAIN, svc))
```

**Why:** Clean service registration, automatic cleanup on unload, consistent pattern.

#### 5. Entity Platform Pattern

```python
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo

class PresetButton(Entity):
    """Button entity for preset activation."""

    _attr_has_entity_name = True

    def __init__(
        self,
        preset_manager: PresetManager,
        preset_config: PresetConfig,
    ) -> None:
        """Initialize button."""
        self._preset_manager = preset_manager
        self._preset_config = preset_config

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_{self._preset_config.preset_id}_button"

    @property
    def name(self) -> str:
        """Return name."""
        return self._preset_config.name
```

**Why:** Unique IDs, proper naming, device grouping, entity registry integration.

### Anti-Patterns (What NOT to Do)

#### ❌ Blocking the Event Loop

```python
# WRONG
data = requests.get(url).json()  # Blocks entire HA

# CORRECT
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

#### ❌ Missing Unique IDs

```python
# WRONG
@property
def unique_id(self) -> str:
    return self._name  # Name can change!

# CORRECT
@property
def unique_id(self) -> str:
    return f"{DOMAIN}_{self._preset_id}_{self._entity_type}"
```

#### ❌ Not Handling Errors

```python
# WRONG
async def async_handle_service(call: ServiceCall):
    result = await controller.ensure_state(...)  # No error handling!

# CORRECT
async def async_handle_service(call: ServiceCall):
    try:
        result = await controller.ensure_state(...)
        return result.to_dict()
    except Exception as err:
        _LOGGER.error("Service failed: %s", err)
        raise HomeAssistantError(f"Failed: {err}") from err
```

#### ❌ YAML Configuration

```python
# WRONG - Don't do this for new integrations
async def async_setup_platform(hass, config, async_add_entities):
    # NO! Use config flow instead
```

---

## Quick Reference

### Essential Commands

```bash
# Makefile Commands (Recommended)
make help               # Show all available commands
make setup              # Initial project setup
make verify             # Verify development environment
make quality            # Run all quality checks
make ci                 # Simulate CI checks locally
make test               # Run all tests
make test-cov           # Run tests with coverage
make lint               # Run Ruff linter
make lint-fix           # Lint with auto-fix
make format             # Format code
make type-check         # Run mypy
make clean              # Remove build artifacts
make info               # Show project information

# Direct Commands (Also Work)
pytest tests/                         # Run all tests
pytest tests/ -v                      # Verbose output
pytest tests/test_controller.py       # Specific file
pytest tests/ --cov=custom_components # With coverage
ruff check custom_components/         # Lint only
ruff check --fix custom_components/   # Lint with auto-fix
ruff format custom_components/        # Format code
mypy custom_components/               # Type check
pre-commit run --all-files            # All hooks

# Git
git checkout testing                  # Switch to testing branch
git add .                             # Stage changes
git commit -m "message"               # Commit (hooks run)
git push                              # Push (CI runs)
```

### Keyboard Shortcuts (VS Code)

| Shortcut       | Action                                     |
| -------------- | ------------------------------------------ |
| `Ctrl+Shift+B` | Run default build task (Quality Check All) |
| `Ctrl+Shift+P` | Command palette → "Tasks: Run Task"        |
| `Ctrl+`\`      | Toggle terminal                            |
| `Ctrl+Shift+M` | Show problems panel                        |

### File Locations Cheat Sheet

```bash
# Agent files
~/.claude/agents/ha-integration-agent.md           # Claude agent
.github/copilot-instructions.md                     # Copilot context
.vscode/codex-instructions.md                       # Codex context

# Documentation
CLAUDE.md                                           # Claude instructions
README.md                                           # Project overview
REFERENCE_GUIDE.md                                  # This file
resources/agents/ha-integration-agent/README.md     # Agent guide

# Automation
.github/workflows/ci.yml                            # CI/CD pipeline
.vscode/tasks.json                                  # VS Code tasks
.pre-commit-config.yaml                             # Git hooks

# Configuration
pyproject.toml                                      # Tool config
.vscode/settings.json                               # Editor settings
```

### Common Issues & Solutions

| Issue                      | Solution                                       |
| -------------------------- | ---------------------------------------------- |
| Import errors              | `source venv/bin/activate` (if using venv)     |
| Tests failing              | `pytest tests/ -v` to see detailed output      |
| Linting errors             | `ruff check --fix custom_components/`          |
| Type errors                | `mypy custom_components/`                      |
| CI failing locally passing | Clear caches, run `pre-commit run --all-files` |
| Pre-commit failing         | `pre-commit run --all-files`                   |

### Quality Checklist

Before committing:

- [ ] `ruff check custom_components/` passes
- [ ] `ruff format custom_components/` passes
- [ ] `mypy custom_components/` passes
- [ ] `pytest tests/` passes
- [ ] No TODO/FIXME comments
- [ ] Tests added for new functionality
- [ ] Type hints on all functions
- [ ] Docstrings on public API

Before creating PR:

- [ ] All quality checks pass
- [ ] Coverage hasn't decreased
- [ ] PR template filled out
- [ ] Breaking changes documented

---

## Troubleshooting

### Environment Issues

#### Problem: Import Errors

```bash
# Symptom
ModuleNotFoundError: No module named 'homeassistant'

# Solution
source venv/bin/activate  # If using venv
pip install -e .
```

#### Problem: Tools Not Found

```bash
# Symptom
bash: ruff: command not found

# Solution
source venv/bin/activate  # If using venv
which ruff  # Should show path
pip install -e .
```

### Testing Issues

#### Problem: Tests Can't Import custom_components

**Symptoms:**

```bash
ModuleNotFoundError: No module named 'custom_components'
ModuleNotFoundError: No module named 'custom_components.ha_light_controller'
```

**Root Causes:**

1. Missing `custom_components/__init__.py` - Python doesn't treat it as a package
2. Project root not in Python path during tests
3. Imports placed inside test functions instead of module level

**Solution:**

```bash
# 1. Ensure __init__.py exists
touch custom_components/__init__.py

# 2. Verify conftest.py setup
cat tests/conftest.py
# Should contain:
#   import sys
#   from pathlib import Path
#   custom_components_path = Path(__file__).parent.parent / "custom_components"
#   sys.path.insert(0, str(custom_components_path.parent))

# 3. Use module-level imports in tests
# CORRECT:
from custom_components.ha_light_controller import PLATFORMS

async def test_platforms():
    assert PLATFORMS is not None

# INCORRECT:
async def test_platforms():
    from custom_components.ha_light_controller import PLATFORMS  # Don't import here!
    assert PLATFORMS is not None

# 4. Run tests
pytest tests/ -v
```

**Why:** Pytest imports test modules during collection phase, before fixtures run.
Module-level imports work correctly, but imports inside test functions execute after
fixture setup, which can cause path resolution issues.

#### Problem: Mypy Type Check Failures

**Symptoms:**

```bash
error: Cannot find implementation or library stub for module named "homeassistant.config_entries"
error: Returning Any from function declared to return "bool"
KeyError: 'setter_type'  # Cache corruption
```

**Root Causes:**

1. Home Assistant type stubs not found by mypy
2. Corrupted mypy cache
3. Pre-commit mypy config differs from mypy.ini

**Solution:**

```bash
# 1. Clear mypy cache (fixes most issues)
rm -rf .mypy_cache

# 2. Verify mypy.ini configuration
cat mypy.ini
# Should contain:
#   [mypy-homeassistant]
#   ignore_missing_imports = True
#
#   [mypy-homeassistant.*]
#   ignore_missing_imports = True

# 3. Update pre-commit config
# In .pre-commit-config.yaml, ensure:
#   - repo: https://github.com/pre-commit/mirrors-mypy
#     hooks:
#       - id: mypy
#         additional_dependencies:
#           - homeassistant  # Must be here!

# 4. Rebuild pre-commit environment
pre-commit clean
pre-commit install

# 5. Test both ways
mypy custom_components/              # Direct mypy
pre-commit run mypy --all-files      # Pre-commit mypy
```

**Why:** Mypy caches type information for performance. Stale caches cause confusing
errors. Pre-commit runs mypy in an isolated environment that needs homeassistant
installed separately.

#### Problem: Coverage Decreased

```bash
# Check what's not covered
pytest tests/ --cov=custom_components --cov-report=html
xdg-open htmlcov/index.html

# Add tests for red lines
# Commit and rerun
```

### Automation Issues

#### Problem: CI Passing Locally But Failing on GitHub

```bash
# Solution: Check Python version
python --version  # Should be 3.14.2 or 3.13+

# Run exact CI checks
make ci             # Simulates CI environment exactly

# Or manually:
ruff check custom_components/
ruff format --check custom_components/
mypy custom_components/
pytest tests/ -v
```

#### Problem: Pre-commit Hooks Not Running

```bash
# Solution
pre-commit install
pre-commit run --all-files
```

#### Problem: Pre-commit Hooks Failing

```bash
# Auto-fix what's possible
pre-commit run --all-files

# If still failing, check specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Fix issues manually, then commit
```

### Git Issues

#### Problem: Large Files in Commit

```bash
# Symptom
Error: File ... is 5.00 MB; this is larger than GitHub's maximum file size

# Solution
# Check .gitignore includes:
venv/
__pycache__/
*.pyc
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Remove from git
git rm --cached path/to/large/file
git commit -m "Remove large file"
```

#### Problem: Merge Conflicts

```bash
# Don't force push or reset unless you understand implications

# Solution
git status
# Edit conflicted files manually
# Remove conflict markers (<<<<, ====, >>>>)
git add .
git commit -m "Resolve merge conflicts"
```

### Agent Issues

#### Problem: Agent Not Responding (Claude Code)

```bash
# Verify installation
ls -lh ~/.claude/agents/ha-integration-agent.md

# Reinstall if missing
cp resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md \
   ~/.claude/agents/ha-integration-agent.md

# Use explicit invocation
Task(subagent_type="ha-integration-agent", prompt="your question")
```

#### Problem: Copilot Not Using Context

```bash
# Verify file exists
ls -lh .github/copilot-instructions.md

# Keep agent files open in tabs
code resources/agents/ha-integration-agent/ha_integration_agent_spec.md

# Use descriptive comments
# Create async light control following HA Bronze tier requirements
```

### Performance Issues

#### Problem: Slow Tests

```bash
# Run specific tests only
pytest tests/test_controller.py -v

# Skip slow tests during development
pytest tests/ -m "not slow"
```

#### Problem: Slow CI

- Caching is enabled in `.github/workflows/ci.yml`
- CI runs on Python 3.14 only (not a matrix)
- Consider splitting tests if they get too large

---

## Additional Resources

### Official Documentation

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Creating Your First Integration](https://developers.home-assistant.io/docs/creating_component_index/)

### Community Resources

- [HA Community Forums - Development](https://community.home-assistant.io/c/development/10)
- [HA Discord - Development Channel](https://discord.gg/home-assistant)

### Integration Documentation

| Document                                                                                              | Purpose                             |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------- |
| [README.md](README.md)                                                                                | Project overview and quick start    |
| [CLAUDE.md](CLAUDE.md)                                                                                | Instructions for Claude Code        |
| [REFERENCE_GUIDE.md](REFERENCE_GUIDE.md)                                                              | Complete reference (this file)      |
| [.github/AUTOMATION_GUIDE.md](.github/AUTOMATION_GUIDE.md)                                            | Detailed automation documentation   |
| [resources/agents/.../README.md](resources/agents/ha-integration-agent/README.md)                     | Agent installation and usage        |
| [resources/agents/.../...spec.md](resources/agents/ha-integration-agent/ha_integration_agent_spec.md) | Comprehensive patterns and examples |

### Getting Help

1. **Check documentation first**
   - This guide
   - Agent README
   - Official HA docs

2. **Use the agent**

   ```
   @agent ha-integration-agent
   I'm having trouble with [specific issue]
   ```

3. **Run verification**

   ```bash
   make verify         # Verify environment
   make quality        # Run all checks
   make ci             # Simulate CI
   ```

4. **Use Makefile commands**

   ```bash
   make info           # Show environment information
   make verify         # Verify development environment
   make ci             # Run all CI checks locally
   ```

5. **Check logs**
   - CI logs on GitHub
   - Local test output
   - Home Assistant logs

6. **Community support**
   - HA Community Forums
   - HA Discord
   - GitHub Issues

---

## Version History

| Date       | Version | Changes                                                 |
| ---------- | ------- | ------------------------------------------------------- |
| 2026-02-07 | 1.0.0   | Initial reference guide created for HA-Light-Controller |
| 2026-02-07 | 1.0.0   | Added AI agent system documentation                     |
| 2026-02-07 | 1.0.0   | Added complete automation infrastructure                |
| 2026-02-07 | 1.0.0   | Added development workflows and troubleshooting         |

---

## Summary

HA-Light-Controller is a production-ready Home Assistant custom integration providing:

✅ **Reliable Light Control**

- State verification and automatic retries
- Comprehensive light parameter support
- Error handling and logging

✅ **Preset Management**

- Create, activate, manage lighting presets
- UI-based configuration flow
- Service-based API for automation

✅ **AI Agent Assistance**

- Claude Code agent installed
- GitHub Copilot integration
- VS Code Codex integration

✅ **Four-Layer Automation**

- GitHub Actions CI/CD
- Pre-commit Git hooks
- VS Code interactive tasks
- Direct CLI commands

✅ **Quality Enforcement**

- Bronze tier minimum enforced
- Automatic linting & formatting
- Type checking with mypy
- Test coverage tracking

✅ **Complete Documentation**

- Agent guides (655 lines)
- Comprehensive spec (750 lines)
- Automation guide (detailed)
- This reference guide

✅ **Best Practices Built-In**

- Config flow requirement
- Async-first architecture
- Full type hints
- Proper error handling

**You have a production-quality Home Assistant integration!** 🚀

---

**Quick Start:**

```bash
make setup          # Initial setup
make quality        # Run all quality checks
make ci             # Simulate CI locally
```

**Need Help?** See [Troubleshooting](#troubleshooting) or ask the agent:

```
@agent ha-integration-agent
Help me with [your task]
```

---

_Last Updated: February 7, 2026_ _Integration Version: 0.2.1_ _Home Assistant Version:
2025.2.0+_ _Python Version: 3.14.2 (minimum 3.13)_
