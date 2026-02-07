# HACS Integration Guide

This guide explains how to publish your Home Assistant custom integration to [HACS (Home Assistant Community Store)](https://hacs.xyz/), the most popular distribution method for custom integrations.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [Creating hacs.json](#creating-hacsjson)
- [Version Management](#version-management)
- [Submission Process](#submission-process)
- [Post-Submission](#post-submission)
- [Common Rejection Reasons](#common-rejection-reasons)
- [Maintenance & Updates](#maintenance--updates)

---

## Prerequisites

Before submitting to HACS, ensure your integration meets these requirements:

### 1. Quality Requirements

- ✅ **Minimum Bronze tier** quality (see [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md))
- ✅ **All tests pass** - No failing tests in CI
- ✅ **Code quality checks pass** - Ruff and mypy with zero errors
- ✅ **Proper error handling** - No unhandled exceptions

### 2. Repository Requirements

- ✅ **Public GitHub repository** - Must be publicly accessible
- ✅ **Clear README.md** - Installation and configuration instructions
- ✅ **License file** - LICENSE or LICENSE.md (recommend MIT, Apache 2.0, or GPL-3.0)
- ✅ **Semantic versioning** - Uses MAJOR.MINOR.PATCH format
- ✅ **GitHub releases** - At least one tagged release

### 3. Code Requirements

- ✅ **Config flow** - UI-based setup (no YAML configuration)
- ✅ **Unique IDs** - All entities have stable unique_id
- ✅ **manifest.json version** - Must include `"version"` field
- ✅ **No code in repo root** - All integration code in `custom_components/your_domain/`

---

## Repository Structure

Your repository must follow this structure:

```
your-integration-repo/
├── custom_components/
│   └── your_integration/          # Domain name from manifest.json
│       ├── __init__.py
│       ├── manifest.json          # Must include "version" field
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
│
├── .github/
│   └── workflows/
│       └── validate.yml            # Optional: HACS validation workflow
│
├── README.md                       # Required
├── LICENSE                         # Required
├── hacs.json                       # Required for HACS
└── .gitignore
```

**Important:** All integration code must be inside `custom_components/your_domain/`. HACS will reject repositories with code outside this directory.

---

## Creating hacs.json

Create a `hacs.json` file in your repository root to configure HACS integration:

### Basic hacs.json

```json
{
  "name": "Your Integration Name",
  "content_in_root": false,
  "homeassistant": "2024.4.0"
}
```

### Complete hacs.json with All Options

```json
{
  "name": "Your Integration Name",
  "content_in_root": false,
  "homeassistant": "2024.4.0",
  "country": ["US", "CA", "GB"],
  "render_readme": true,
  "persistent_directory": "storage",
  "iot_class": "local_polling",
  "zip_release": false
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name shown in HACS (can differ from domain) |
| `content_in_root` | Yes | Always `false` for integrations (code is in `custom_components/`) |
| `homeassistant` | Yes | Minimum Home Assistant version required (e.g., "2024.4.0") |
| `country` | No | List of country codes where integration is relevant |
| `render_readme` | No | Set to `true` to render README.md in HACS UI |
| `persistent_directory` | No | Directory name for persistent data storage |
| `iot_class` | No | IoT class from manifest.json (for display) |
| `zip_release` | No | Set to `true` if you provide ZIP releases |

### Determining homeassistant Version

Use the **oldest Home Assistant version** your integration supports:

```python
# Check what HA features you use and when they were introduced
# Common version milestones:
# 2024.4.0 - Python 3.12 minimum
# 2024.11.0 - Python 3.12.4 minimum
# 2025.2.0 - Python 3.13 minimum

# Conservative approach: Test on oldest version you claim to support
```

**Tip:** Use `homeassistant >= MAJOR.MINOR.0` format (patch version 0) unless you need a specific patch.

---

## Version Management

HACS requires proper version management using semantic versioning.

### Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)

- **MAJOR** - Incompatible API changes, breaking changes
- **MINOR** - New features, backward-compatible
- **PATCH** - Bug fixes, backward-compatible

### Updating manifest.json

**Always update the version in manifest.json before releasing:**

```json
{
  "domain": "your_integration",
  "name": "Your Integration",
  "version": "1.2.3",
  "...": "..."
}
```

### Creating GitHub Releases

1. **Tag your commit** with the version number:
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```

2. **Create GitHub release:**
   - Go to repository → Releases → "Draft a new release"
   - Select tag: `v1.2.3`
   - Release title: `v1.2.3` or descriptive name
   - Description: Changelog for this version

3. **Update CHANGELOG.md** (recommended):
   ```markdown
   ## [1.2.3] - 2026-02-07
   ### Added
   - New temperature sensor entity

   ### Fixed
   - Connection timeout handling
   ```

**Tag Format:** Use `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`) consistently.

---

## Submission Process

### Step 1: Validate Your Repository

Use the [HACS Action](https://github.com/hacs/action) to validate your repository:

Create `.github/workflows/validate.yml`:

```yaml
name: Validate

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: HACS Validation
        uses: hacs/action@main
        with:
          category: integration
```

Run this workflow and fix any validation errors before submitting.

### Step 2: Submit to HACS

1. **Go to** https://github.com/hacs/default/issues/new/choose

2. **Select** "Add integration" template

3. **Fill out the form:**
   - Repository URL: `https://github.com/yourusername/your-integration`
   - Domain: `your_integration` (from manifest.json)
   - Brief description
   - Confirm all requirements met

4. **Submit the issue**

5. **Wait for review** (typically 1-7 days)

### Step 3: Address Review Feedback

HACS maintainers will review your submission and may request changes:

- Code quality improvements
- Documentation updates
- Bug fixes
- Validation errors

Respond promptly and make requested changes.

### Step 4: Approval

Once approved:
- Your integration appears in HACS
- Users can install via HACS UI
- Automatic update notifications for new releases

---

## Post-Submission

### Installation Instructions for Users

After HACS approval, users install via:

1. HACS → Integrations → "Explore & Download Repositories"
2. Search for "Your Integration Name"
3. Click "Download"
4. Restart Home Assistant
5. Add integration via Settings → Devices & Services

**Update your README.md** with HACS installation instructions.

### Monitoring Usage

HACS provides download statistics:
- Check https://github.com/hacs/integration for metrics
- Monitor issues for user feedback
- Track release downloads on GitHub

---

## Common Rejection Reasons

### 1. Missing `version` in manifest.json

**Error:** "Integration does not have a version in manifest.json"

**Fix:**
```json
{
  "domain": "your_integration",
  "version": "1.0.0"
}
```

### 2. No GitHub Releases

**Error:** "Repository has no releases"

**Fix:**
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
# Create release on GitHub from this tag
```

### 3. Code Outside custom_components/

**Error:** "Integration code must be in custom_components/"

**Fix:** Move all `.py` files into `custom_components/your_domain/`

### 4. Breaking Changes Without Migration

**Error:** "Breaking change requires migration path or major version bump"

**Fix:**
- Implement `async_migrate_entry()` in `__init__.py`
- **OR** bump major version (e.g., 1.x.x → 2.0.0)
- Document migration in release notes

### 5. Security Vulnerabilities

**Error:** "Security issue found: credentials logged"

**Fix:** Review [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) and fix:
- Remove credential logging
- Mask sensitive data
- Use proper secret storage

### 6. Incomplete Documentation

**Error:** "README.md lacks installation/configuration instructions"

**Fix:** Add sections:
- Installation via HACS
- Configuration via UI
- Troubleshooting
- Support/contact info

### 7. Non-functional Integration

**Error:** "Integration fails to load in Home Assistant"

**Fix:**
- Test installation on clean HA instance
- Fix import errors
- Resolve missing dependencies
- Ensure config flow works

---

## Maintenance & Updates

### Releasing Updates

1. **Make changes** in your codebase
2. **Update version** in `manifest.json`
3. **Update CHANGELOG.md**
4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Release v1.2.4: Fix connection timeout"
   ```
5. **Create tag:**
   ```bash
   git tag -a v1.2.4 -m "Release v1.2.4"
   git push origin v1.2.4
   ```
6. **Create GitHub release** with changelog

HACS users will automatically see update notifications.

### Breaking Changes

If you introduce breaking changes:

**Option 1: Provide Migration**
```python
async def async_migrate_entry(hass, config_entry):
    """Migrate old entry."""
    if config_entry.version == 1:
        # Migrate version 1 to version 2
        new_data = {**config_entry.data}
        new_data["new_field"] = "default_value"

        config_entry.version = 2
        hass.config_entries.async_update_entry(
            config_entry, data=new_data
        )

    return True
```

**Option 2: Bump Major Version**
- Increment major version (e.g., 1.x.x → 2.0.0)
- Document breaking changes in release notes
- Provide migration instructions for users

### Deprecation Policy

When removing features:

1. **Announce deprecation** in version N
2. **Mark as deprecated** with warnings in logs
3. **Remove feature** in version N+1 (minimum 6 months later)

Example:
```python
_LOGGER.warning(
    "The 'old_field' configuration is deprecated and will be "
    "removed in version 2.0.0. Use 'new_field' instead."
)
```

---

## Checklist: HACS Submission Readiness

Use this checklist before submitting:

- [ ] Bronze tier quality achieved (see [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md))
- [ ] Public GitHub repository
- [ ] LICENSE file present
- [ ] README.md with installation/configuration instructions
- [ ] `manifest.json` includes `"version"` field
- [ ] At least one GitHub release created
- [ ] `hacs.json` created in repository root
- [ ] Code only in `custom_components/your_domain/`
- [ ] HACS validation workflow passes (if added)
- [ ] Config flow implemented (no YAML setup)
- [ ] All entities have unique IDs
- [ ] Tests pass in CI
- [ ] No security vulnerabilities
- [ ] Changelog or release notes provided

---

## Resources

- **HACS Documentation**: https://hacs.xyz/docs/publish/start
- **HACS Action**: https://github.com/hacs/action
- **HACS Default Repository**: https://github.com/hacs/default
- **Semantic Versioning**: https://semver.org/
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github

## Getting Help

- **HACS Discord**: https://discord.gg/apgchf8
- **Home Assistant Community**: https://community.home-assistant.io/
- **HACS Issues**: https://github.com/hacs/integration/issues

---

**Ready to publish?** Follow this guide step-by-step, and your integration will be available to thousands of Home Assistant users through HACS!
