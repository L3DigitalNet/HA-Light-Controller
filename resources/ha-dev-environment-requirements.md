# Home Assistant Integration Development Environment Requirements

This document defines the required development environment for creating Home Assistant integrations that meet or exceed the Integration Quality Scale standards.

## Table of Contents

- [Python Requirements](#python-requirements)
- [Development Environment Options](#development-environment-options)
- [Core Dependencies](#core-dependencies)
- [Development Tools](#development-tools)
- [Testing Framework](#testing-framework)
- [Code Quality Tools](#code-quality-tools)
- [IDE Setup](#ide-setup)
- [Optional Tools](#optional-tools)
- [Verification Checklist](#verification-checklist)

---

## Python Requirements

### Version Requirements

**Current Standard (as of 2025):**
- **Python 3.13+** is required for Home Assistant 2025.2 and later
- Development environment should use **Python 3.14.2 or higher** to avoid compatibility issues
- Home Assistant maintains support for the latest two minor Python versions per ADR-0002

**Important Notes:**
- All integration code must be compatible with Python 3.13+
- Use modern type syntax: `list[str]` instead of `List[str]`, `dict[str, Any]` instead of `Dict[str, Any]`
- All I/O operations must be asynchronous (never block the event loop)
- Use `from __future__ import annotations` in every Python file

### Package Manager

**Recommended: UV**
- Modern, fast Python package manager
- Better dependency resolution than pip
- Improved virtual environment management

**Alternative: pip**
- Traditional package manager (minimum requirement)
- Ensure pip is up-to-date: `pip install --upgrade pip`

---

## Development Environment Options

### Option 1: DevContainer (Recommended)

**Prerequisites:**
- Docker Desktop or Docker Engine
- Visual Studio Code
- Remote - Containers extension for VS Code

**Advantages:**
- Pre-configured development environment
- Debugging support enabled by default
- Consistent across all developers
- Isolated from host system

**Limitations:**
- May face challenges exposing hardware (USB devices, adapters) on Windows/macOS
- Requires Docker knowledge
- Higher resource usage

**Setup:**
```bash
# Clone the integration blueprint
git clone https://github.com/ludeeus/integration_blueprint
cd integration_blueprint

# Open in VS Code
code .

# VS Code will prompt to "Reopen in Container"
# Accept to launch the containerized environment
```

### Option 2: Local Virtual Environment

**Prerequisites:**
- Python 3.14.2 or higher
- Git
- Operating system-specific build tools (see below)

**OS-Specific Dependencies:**

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-venv \
    build-essential \
    autoconf \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libffi-dev \
    libudev-dev \
    zlib1g-dev \
    ffmpeg
```

#### Fedora
```bash
sudo dnf install -y \
    python3-devel \
    gcc \
    gcc-c++ \
    autoconf \
    openssl-devel \
    libxml2-devel \
    libxslt-devel \
    libjpeg-turbo-devel \
    libffi-devel \
    systemd-devel \
    zlib-devel \
    ffmpeg-free-devel
```

#### Arch/Manjaro
```bash
sudo pacman -S --noconfirm \
    base-devel \
    python \
    autoconf \
    ffmpeg
```

#### macOS
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 autoconf ffmpeg cmake
```

#### Windows
**Use Windows Subsystem for Linux (WSL):**
1. Install WSL 2 with Ubuntu
2. Follow Ubuntu dependency installation steps above
3. **Important:** Keep all code within WSL filesystem to avoid permission issues

**Setup Commands:**
```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate  # On Windows WSL: same command

# Install Home Assistant for development
pip install homeassistant

# Install development tools (see sections below)
```

---

## Core Dependencies

### Home Assistant Core

**Installation:**
```bash
pip install homeassistant
```

This provides:
- Home Assistant framework
- Core API and helpers
- Base entity classes
- Config entry system
- Event loop infrastructure

### Required Python Libraries

**Async HTTP (for API integrations):**
```bash
pip install aiohttp
```

**Schema Validation:**
```bash
pip install voluptuous
```
- Used for config flow validation
- Required for user input schemas

**Additional Common Dependencies:**
- `aiodns` - Async DNS resolution
- `async-timeout` - Timeout handling for async operations
- `python-slugify` - Safe string slugification

---

## Development Tools

### Essential Development Tools

**Git:**
```bash
# Ubuntu/Debian
sudo apt-get install git

# Fedora
sudo dnf install git

# macOS
brew install git
```

**Code Editor (VS Code recommended):**
- Download from https://code.visualstudio.com/
- Provides excellent Python support
- Integrates with DevContainer setup
- Available for all major platforms

### Repository Setup

```bash
# Fork the Home Assistant Core repository (for core contributions)
# Or use integration_blueprint for custom integrations

# Clone your fork
git clone https://github.com/YOUR_USERNAME/core.git
cd core

# Add upstream remote
git remote add upstream https://github.com/home-assistant/core.git

# Run setup script (creates venv, installs dependencies)
script/setup

# Activate environment
source venv/bin/activate

# Start Home Assistant in development mode
hass -c config
```

---

## Testing Framework

### Required Testing Tools

**pytest (Primary test runner):**
```bash
pip install pytest pytest-asyncio
```

**pytest-homeassistant-custom-component:**
```bash
pip install pytest-homeassistant-custom-component
```
- Provides `hass` fixture
- Mocks Home Assistant infrastructure
- No running HA instance needed

**Coverage Tools:**
```bash
pip install pytest-cov
```

### Test Directory Structure

Required for Bronze tier on Integration Quality Scale:

```
tests/
├── conftest.py           # Shared fixtures and mocks
├── test_config_flow.py   # Config flow tests (MANDATORY)
├── test_init.py          # Setup/unload tests
├── test_sensor.py        # Sensor platform tests
└── test_coordinator.py   # Coordinator tests
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config_flow.py -v

# Run with coverage report
pytest tests/ --cov=custom_components.{domain} --cov-report=html

# Run single test
pytest tests/test_config_flow.py::test_user_flow_success -v
```

**Minimum Test Requirements (Bronze Tier):**
- Config flow success test
- Config flow connection error test
- Config flow authentication error test
- Config flow duplicate prevention test

---

## Code Quality Tools

### Linting and Formatting

**Ruff (Official HA linter/formatter):**
```bash
pip install ruff
```

Home Assistant uses Ruff for both linting and formatting:

```bash
# Run linter
ruff check custom_components/{domain}/ --fix

# Run formatter
ruff format custom_components/{domain}/

# Check without fixing
ruff check custom_components/{domain}/
```

**Configuration:**
Create `pyproject.toml` or `.ruff.toml` for project-specific settings.

### Type Checking

**mypy (Type checker):**
```bash
pip install mypy
```

**Usage:**
```bash
# Type check your integration
mypy custom_components/{domain}/

# Must pass with 0 errors for Gold tier
```

**Configuration (pyproject.toml):**
```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pre-commit Hooks (Optional but Recommended)

```bash
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Example `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

---

## IDE Setup

### Visual Studio Code (Recommended)

**Required Extensions:**
- **Python** (ms-python.python) - Python language support
- **Pylance** (ms-python.vscode-pylance) - Fast, feature-rich language server
- **Remote - Containers** (ms-vscode-remote.remote-containers) - DevContainer support

**Recommended Extensions:**
- **Home Assistant Config Helper** (keesschollaart.vscode-home-assistant) - YAML validation
- **Ruff** (charliermarsh.ruff) - Native Ruff integration
- **GitLens** (eamodio.gitlens) - Enhanced Git capabilities
- **Error Lens** (usernamehw.errorlens) - Inline error display

**VS Code Settings (`.vscode/settings.json`):**
```json
{
  "python.analysis.typeCheckingMode": "strict",
  "python.linting.enabled": true,
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

### PyCharm/IntelliJ IDEA

**Setup:**
1. Open project in PyCharm
2. Configure Python interpreter to use virtual environment
3. Enable pytest as test runner
4. Configure Ruff as external tool

**Plugins:**
- **Home Assistant** - YAML support and validation
- **Ruff** - Linting integration

---

## Optional Tools

### Documentation Generation

**MkDocs (for project documentation):**
```bash
pip install mkdocs mkdocs-material
```

### API Development

**Postman or HTTPie:**
```bash
# HTTPie for CLI API testing
pip install httpie

# Usage
http GET http://localhost:8123/api/states
```

### Monitoring and Debugging

**Home Assistant CLI:**
```bash
pip install homeassistant-cli

# Usage
hass-cli --server http://localhost:8123 state list
```

**HA Debug Mode:**
```bash
# Start HA with debug logging
hass -c config --debug

# Or set in configuration.yaml:
logger:
  default: info
  logs:
    custom_components.{domain}: debug
```

### Claude Code Skills (Development Assistance)

Install the provided HA development skills for AI-assisted development:

```bash
# Project-level installation (recommended)
cp -r resources/skills/ha-skills ~/.claude/skills/

# Or user-level installation
./resources/skills/install.sh user
```

**Available Skills:**
- `ha-integration-scaffold` - Generate integration structure
- `ha-config-flow` - Config flow implementation
- `ha-coordinator` - DataUpdateCoordinator patterns
- `ha-entity-platforms` - Entity platform creation
- `ha-testing` - Test writing guidance
- `ha-debugging` - Troubleshooting assistance
- `ha-async-patterns` - Async Python patterns

---

## Verification Checklist

Use this checklist to verify your development environment is properly configured:

### Python Environment
- [ ] Python 3.14.2+ installed
- [ ] Virtual environment created and activated
- [ ] `homeassistant` package installed
- [ ] Python version verified: `python --version`

### Core Tools
- [ ] Git installed and configured
- [ ] Code editor (VS Code) installed
- [ ] Ruff installed: `ruff --version`
- [ ] mypy installed: `mypy --version`
- [ ] pytest installed: `pytest --version`

### Testing
- [ ] `pytest-homeassistant-custom-component` installed
- [ ] `pytest-asyncio` installed
- [ ] Sample test runs successfully
- [ ] Coverage reporting works

### IDE Configuration
- [ ] Python extension installed (VS Code)
- [ ] Pylance installed (VS Code)
- [ ] Type checking enabled in editor
- [ ] Format on save configured
- [ ] Pytest test discovery working

### Optional Enhancements
- [ ] Pre-commit hooks installed
- [ ] Claude Code HA skills installed
- [ ] Home Assistant running in dev mode
- [ ] Debug logging configured

### Integration Development Readiness
- [ ] Can create custom_components directory structure
- [ ] Can run Home Assistant with: `hass -c config`
- [ ] Can access HA at http://localhost:8123
- [ ] Can view logs: `tail -f config/home-assistant.log`
- [ ] Can run integration tests
- [ ] Can use Ruff to lint/format code
- [ ] Can type check with mypy

---

## Quick Start Commands

### Initial Setup
```bash
# Create project directory
mkdir -p custom_components/{domain}
cd custom_components/{domain}

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install homeassistant pytest pytest-homeassistant-custom-component ruff mypy

# Create test directory
mkdir tests
```

### Daily Development Workflow
```bash
# Activate environment
source venv/bin/activate

# Start HA in debug mode (terminal 1)
hass -c config --debug

# Watch logs (terminal 2)
tail -f config/home-assistant.log | grep {domain}

# Run tests (terminal 3)
pytest tests/ -v

# Lint and format
ruff check . --fix
ruff format .
mypy custom_components/{domain}/
```

### Restart Integration (within HA)
```yaml
# Developer Tools > Services
Service: homeassistant.reload_config_entry
Entity: {your_integration_entity}
```

---

## Additional Resources

### Official Documentation
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Creating Your First Integration](https://developers.home-assistant.io/docs/creating_component_index/)
- [Python Version Policy (ADR-0002)](https://github.com/home-assistant/architecture/blob/master/adr/0002-minimum-supported-python-version.md)

### Community Resources
- [Home Assistant Community Forums - Development](https://community.home-assistant.io/c/development/10)
- [Integration Blueprint Repository](https://github.com/ludeeus/integration_blueprint)
- [Integration Examples Repository](https://github.com/msp1974/HAIntegrationExamples)

### This Repository
- `/resources/skills/` - Claude Code development skills
- `/resources/agents/` - HA integration development agents
- Example integration code in `/resources/agents/ha-integration-agent/`

---

## Troubleshooting

### Common Issues

**ImportError for homeassistant modules:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall homeassistant
pip install --upgrade homeassistant
```

**Tests fail with fixture errors:**
```bash
# Install test dependencies
pip install pytest-homeassistant-custom-component pytest-asyncio
```

**Mypy type check failures:**
```bash
# Install type stubs
pip install types-requests types-aiofiles
```

**Ruff not found:**
```bash
# Install Ruff
pip install ruff

# Verify installation
ruff --version
```

**Home Assistant won't start:**
```bash
# Check Python version
python --version  # Should be 3.14.2+

# Check for dependency issues
pip check

# Start with debug logging
hass -c config --debug
```

---

## Conclusion

This development environment provides everything needed to create high-quality Home Assistant integrations that meet Bronze tier requirements (minimum for custom integrations) and can scale to Platinum tier (excellence standard).

**Next Steps:**
1. Set up your development environment using this guide
2. Complete the verification checklist
3. Review the `/resources/skills/` documentation for integration patterns
4. Start developing using the integration blueprint or scaffolding tools

**Integration Quality Goals:**
- **Bronze**: Basic functionality with config flow and tests
- **Silver**: Robust error handling and reliability
- **Gold**: Full async implementation with comprehensive testing
- **Platinum**: Exemplary code quality and documentation
