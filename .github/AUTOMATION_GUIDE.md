# Automation Guide

This template includes comprehensive automation and tooling to ensure high-quality Home Assistant integrations.

## Table of Contents

- [GitHub Actions CI/CD](#github-actions-cicd)
- [VS Code Tasks](#vs-code-tasks)
- [Makefile Commands](#makefile-commands)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Dependabot](#dependabot)
- [Issue Templates](#issue-templates)

---

## GitHub Actions CI/CD

### Overview

The CI pipeline runs automatically on:
- Push to `main` or `testing` branches
- Pull requests to `main` or `testing`
- Manual workflow dispatch

### Workflow Jobs

#### 1. **Lint** (`lint`)
- Runs Ruff linter on all Python code
- Checks code formatting compliance
- **Status:** ✅ Must pass for PR approval

**Commands run:**
```bash
ruff check custom_components/ tests/ scripts/
ruff format --check custom_components/ tests/ scripts/
```

#### 2. **Type Check** (`type-check`)
- Runs mypy type checker
- Validates type hints and type safety
- **Status:** ✅ Must pass for PR approval

**Commands run:**
```bash
mypy custom_components/
```

#### 3. **Test** (`test`)
- Runs pytest test suite
- Matrix tests on Python 3.13 and 3.14
- Generates coverage reports
- Uploads coverage to Codecov (if configured)
- **Status:** ✅ Must pass for PR approval

**Commands run:**
```bash
pytest tests/ --cov=custom_components --cov-report=xml --cov-report=term-missing -v
```

#### 4. **Verify Environment** (`verify-environment`)
- Runs environment verification script
- Ensures all dependencies are installed
- Validates project structure
- **Status:** ✅ Must pass for PR approval

**Commands run:**
```bash
python scripts/verify_environment.py
```

#### 5. **All Checks** (`all-checks`)
- Final gate that ensures all jobs passed
- Blocks merging if any check fails

### Configuration

**File:** `.github/workflows/ci.yml`

**Caching:** Pip dependencies are cached for faster builds

**Python Versions:** 3.13 (primary), 3.14 (compatibility check)

### Setting Up Codecov (Optional)

1. Sign up at https://codecov.io/
2. Add your repository
3. Get the upload token
4. Add as GitHub secret: `CODECOV_TOKEN`
5. Coverage reports will be automatically uploaded

---

## VS Code Tasks

### Quick Access

Press `Ctrl+Shift+B` (Linux/Windows) or `Cmd+Shift+B` (Mac) to open the task menu.

### Available Tasks

| Task | Shortcut | Description |
|------|----------|-------------|
| **Quality Check (All)** | `Ctrl+Shift+B` → Default | Runs lint, format, type-check, and tests |
| **Run All Tests** | Test menu | Runs all tests with pytest |
| **Run Tests with Coverage** | Task menu | Runs tests and generates HTML coverage report |
| **Lint with Ruff** | Task menu | Checks code for issues |
| **Lint and Fix with Ruff** | Task menu | Auto-fixes linting issues |
| **Format with Ruff** | Task menu | Formats code |
| **Type Check with mypy** | Task menu | Checks type hints |
| **Run Pre-commit Hooks** | Task menu | Runs all pre-commit hooks |
| **Verify Environment** | Task menu | Verifies development environment |
| **Open Coverage Report** | Task menu | Opens HTML coverage report in browser |

### Using Tasks

#### From Command Palette
1. Press `Ctrl+Shift+P` (Linux/Windows) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select the task you want to run

#### From Terminal Menu
1. Click "Terminal" in the top menu
2. Select "Run Task..."
3. Choose your task

#### Default Build Task
Press `Ctrl+Shift+B` to run the default build task (Quality Check - All)

### Task Configuration

**File:** `.vscode/tasks.json`

**Problem Matchers:** Integrated for Ruff, mypy, and pytest to show errors inline

---

## Makefile Commands

### Quick Reference

```bash
make help              # Show all available commands
make setup             # Initial project setup
make verify            # Verify environment
make quality           # Run all quality checks
make test              # Run tests
make test-cov          # Run tests with coverage
make ci                # Simulate CI locally
```

### All Commands

| Command | Description |
|---------|-------------|
| `make help` | Show help with all available commands |
| `make verify` | Verify development environment |
| `make test` | Run all tests |
| `make test-cov` | Run tests with HTML coverage report |
| `make test-specific FILE=path` | Run specific test file |
| `make lint` | Run Ruff linter (check only) |
| `make lint-fix` | Run Ruff linter with auto-fix |
| `make format` | Format code with Ruff |
| `make type-check` | Run mypy type checker |
| `make pre-commit` | Run pre-commit hooks on all files |
| `make quality` | Run all quality checks (lint, format, type, test) |
| `make clean` | Remove build artifacts and cache files |
| `make install` | Install dependencies |
| `make setup` | Complete project setup (install + hooks) |
| `make new-integration NAME=x` | Create new integration from template |
| `make list-integrations` | List all integrations |
| `make coverage-report` | Open HTML coverage report in browser |
| `make ci` | Simulate CI checks locally |
| `make watch-test` | Auto-run tests on file changes (requires entr) |
| `make info` | Show project information |

### Examples

#### Create a New Integration
```bash
make new-integration NAME=my_thermostat
# Creates custom_components/my_thermostat/ from template
```

#### Run Quality Checks Before Commit
```bash
make quality
# Runs: lint-fix → format → type-check → test
```

#### Simulate CI Locally
```bash
make ci
# Runs all checks exactly as CI does
```

#### Watch Tests (Development Mode)
```bash
make watch-test
# Auto-runs tests when files change
# Requires: sudo apt install entr
```

---

## Pre-commit Hooks

### Overview

Pre-commit hooks run automatically on `git commit` to catch issues before they reach CI.

### Installed Hooks

1. **trailing-whitespace** - Removes trailing whitespace
2. **end-of-file-fixer** - Ensures files end with newline
3. **check-yaml** - Validates YAML syntax
4. **check-added-large-files** - Prevents large files (>500KB)
5. **check-merge-conflict** - Detects merge conflict markers
6. **Ruff** - Lints and auto-fixes Python code
7. **Ruff Format** - Formats Python code
8. **mypy** - Type checks Python code

### Configuration

**File:** `.pre-commit-config.yaml`

### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files custom_components/my_integration/*.py

# Run specific hook
pre-commit run ruff --all-files
```

### Skip Hooks (Emergency Only)

```bash
# Skip all hooks (NOT RECOMMENDED)
git commit --no-verify -m "Emergency fix"

# Better: Fix the issues instead
pre-commit run --all-files
git add .
git commit -m "Fixed linting issues"
```

### Updating Hooks

```bash
# Update hook versions
pre-commit autoupdate

# Reinstall hooks
pre-commit clean
pre-commit install
```

---

## Dependabot

### Overview

Dependabot automatically creates PRs to keep dependencies up-to-date.

### Configuration

**File:** `.github/dependabot.yml`

**Schedule:** Weekly on Mondays at 9:00 AM

**Ecosystems:**
1. **pip** - Python dependencies
2. **github-actions** - GitHub Actions versions

### Dependency Groups

#### Home Assistant Dependencies
- homeassistant
- aiohttp
- voluptuous

#### Testing Dependencies
- pytest*
- pytest-asyncio
- pytest-homeassistant-custom-component
- pytest-cov

#### Code Quality
- ruff
- mypy
- pre-commit

### Customization

Edit `.github/dependabot.yml`:

```yaml
# Change schedule
schedule:
  interval: "daily"  # or "weekly", "monthly"
  day: "monday"
  time: "09:00"

# Change PR limit
open-pull-requests-limit: 5

# Add reviewers
reviewers:
  - "your-github-username"
```

**⚠️ TODO:** Update `your-github-username` in dependabot.yml

---

## Issue Templates

### Available Templates

#### 1. Bug Report
**File:** `.github/ISSUE_TEMPLATE/bug_report.yml`

**Collects:**
- Bug description
- Steps to reproduce
- Expected behavior
- Log output
- HA version, integration version, Python version
- Configuration (sanitized)

#### 2. Feature Request
**File:** `.github/ISSUE_TEMPLATE/feature_request.yml`

**Collects:**
- Problem description
- Proposed solution
- Alternatives considered
- Affected entity platforms
- Willingness to contribute

#### 3. Config
**File:** `.github/ISSUE_TEMPLATE/config.yml`

**Provides links to:**
- Home Assistant Community Forum
- Official HA Developer Documentation
- Integration Quality Scale guide

### Creating Issues

When users click "New Issue" on GitHub, they'll see:
- 📋 Bug Report
- ✨ Feature Request
- 🔗 Links to community resources

---

## Pull Request Template

### Overview

**File:** `.github/pull_request_template.md`

Guides contributors through:
1. Description and issue reference
2. Type of change
3. Quality tier target
4. Testing verification
5. Comprehensive checklist

### Checklist Sections

- **Code Quality** (style, self-review, type hints)
- **Testing** (unit tests, coverage)
- **Async Requirements** (no blocking operations)
- **DataUpdateCoordinator** (if applicable)
- **Entities** (unique IDs, availability)
- **Config Flow** (no YAML)
- **Documentation** (README, docstrings)
- **Pre-commit Hooks** (all passing)

### Review Process

1. Create PR from `testing` → `main`
2. Fill out template completely
3. Check all applicable boxes
4. CI runs automatically
5. Reviewers check against checklist
6. Merge when all checks pass

---

## Best Practices

### Before Committing

```bash
# Option 1: Use Makefile
make quality

# Option 2: Use pre-commit directly
pre-commit run --all-files

# Option 3: VS Code task
# Press Ctrl+Shift+B → "Quality Check (All)"
```

### Before Creating PR

```bash
# Simulate CI locally
make ci

# Or use VS Code task
# Terminal → Run Task → "Quality Check (All)"

# Verify environment
make verify
```

### During Development

```bash
# Watch mode (auto-run tests)
make watch-test

# Quick test iteration
pytest tests/test_specific.py -v

# Type check only
make type-check
```

### When Reviewing PRs

1. ✅ All CI checks pass
2. ✅ PR template filled out
3. ✅ Changes align with Integration Quality Scale
4. ✅ Tests added for new functionality
5. ✅ Documentation updated if needed

---

## Troubleshooting

### CI Failing but Local Passes

**Cause:** Environment differences

**Solution:**
```bash
# Clean caches
make clean

# Reinstall dependencies
pip install --force-reinstall homeassistant

# Run CI simulation
make ci
```

### Pre-commit Hooks Failing

**Cause:** Code doesn't meet standards

**Solution:**
```bash
# Auto-fix what's possible
pre-commit run --all-files

# Manual fixes
make lint-fix
make format

# Commit again
git add .
git commit -m "Fixed linting issues"
```

### Dependabot PRs Failing

**Cause:** Dependency updates broke tests

**Solution:**
1. Review the changelog of the updated package
2. Update code to be compatible
3. Update tests if API changed
4. Merge when CI passes

### Coverage Decreased

**Cause:** New code without tests

**Solution:**
```bash
# Check coverage report
make test-cov
make coverage-report

# Add tests for uncovered lines
# Commit and push
```

### Mypy Type Check Errors with Home Assistant

**Cause:** Mypy can't find Home Assistant type stubs, or cache is corrupted

**Symptoms:**
- `error: Cannot find implementation or library stub for module named "homeassistant.*"`
- `KeyError: 'setter_type'` (cache corruption)
- Inconsistent results between manual mypy runs and pre-commit hooks

**Solution:**
```bash
# 1. Clear mypy cache (fixes most issues)
rm -rf .mypy_cache

# 2. Verify mypy.ini configuration exists
cat mypy.ini  # Should have [mypy-homeassistant.*] with ignore_missing_imports

# 3. Check pre-commit config includes homeassistant
grep -A 5 "id: mypy" .pre-commit-config.yaml
# Should have homeassistant in additional_dependencies

# 4. Update pre-commit environments
pre-commit clean
pre-commit install

# 5. Test
mypy custom_components/
```

**Why this happens:**
- Home Assistant's type stubs aren't always available in mypy's typeshed
- mypy caches type information, and stale caches cause mysterious errors
- Pre-commit runs mypy in an isolated environment that needs homeassistant installed

### Tests Can't Import custom_components

**Cause:** Python path doesn't include the project root, or custom_components isn't a package

**Symptoms:**
- `ModuleNotFoundError: No module named 'custom_components'`
- `ModuleNotFoundError: No module named 'custom_components.your_integration'`
- Tests work individually but fail in pytest collection

**Solution:**
```bash
# 1. Ensure custom_components/__init__.py exists
touch custom_components/__init__.py

# 2. Check conftest.py adds path to sys.path
cat tests/conftest.py | grep -A 3 "sys.path"
# Should have: sys.path.insert(0, str(custom_components_path.parent))

# 3. Use module-level imports in tests (not inside test functions)
# GOOD:
# from custom_components.example_integration import PLATFORMS
# async def test_something():
#     assert PLATFORMS is not None
#
# BAD:
# async def test_something():
#     from custom_components.example_integration import PLATFORMS  # Don't do this

# 4. Run tests with PYTHONPATH
PYTHONPATH=. pytest tests/ -v
```

**Why this happens:**
- Without `__init__.py`, Python doesn't treat custom_components as a package
- Pytest needs the project root in sys.path to find custom_components
- Imports inside async test functions happen after fixture setup, causing path issues

### Pre-commit Hooks Pass but CI Fails (or vice versa)

**Cause:** Pre-commit uses isolated environments with different configurations

**Symptoms:**
- `mypy` passes locally but fails in CI (or opposite)
- Type errors appear only in pre-commit or only in CI
- Different error messages from the same tool

**Solution:**
```bash
# 1. Check if pre-commit config overrides tool configs
cat .pre-commit-config.yaml

# Look for args that override configs:
# BAD: args: [--strict, --ignore-missing-imports]  # Overrides mypy.ini
# GOOD: No args, or only non-conflicting ones

# 2. Ensure pre-commit has same dependencies as CI
# In .pre-commit-config.yaml:
# additional_dependencies:
#   - homeassistant  # Must match CI dependencies

# 3. Rebuild pre-commit environments
pre-commit clean
pre-commit install
pre-commit run --all-files

# 4. Compare with CI
make ci
```

**Why this happens:**
- Pre-commit runs tools in isolated virtualenvs
- Command-line args in `.pre-commit-config.yaml` override config files
- Different dependency versions between environments cause different behavior

---

## Summary

This template provides **four ways** to run quality checks:

1. **GitHub Actions** - Automatic on push/PR
2. **Pre-commit Hooks** - Automatic on commit
3. **VS Code Tasks** - Interactive in editor
4. **Makefile** - Command-line interface

Choose the method that fits your workflow! All ensure Bronze tier quality minimum. 🚀
