# Security Policy

## About This Integration

This is a **custom integration** for Home Assistant providing reliable light control
with state verification, automatic retries, and preset management. Security
considerations apply to:

1. The integration code itself (services, entities, controllers)
2. User data stored in ConfigEntry (presets, settings)

## Supported Versions

This integration follows a rolling release model. Security updates are applied to:

| Version              | Supported | Status             |
| -------------------- | --------- | ------------------ |
| Latest (main branch) | ✅        | Active development |
| Previous commits     | ❌        | Use latest instead |

**Recommendation:** Always use the latest version from the `main` branch.

## Security Considerations

### For Integration Users

When using this integration:

**✅ DO:**

- Store credentials in `ConfigEntry.data` (encrypted by Home Assistant)
- Use HTTPS for all external API communications
- Validate all user inputs in config flows
- Handle authentication errors properly (`ConfigEntryAuthFailed`)
- Follow the security best practices in
  [docs/SECURITY_BEST_PRACTICES.md](docs/SECURITY_BEST_PRACTICES.md)

**❌ DON'T:**

- Log credentials, API keys, or tokens
- Store sensitive data in entity attributes
- Hardcode secrets in source code
- Skip input validation
- Use HTTP for credential transmission

### For Integration Maintainers

Security concerns for the integration repository itself:

**Protected:**

- ✅ GitHub Actions workflows use explicit permissions
- ✅ Dependabot enabled for dependency updates
- ✅ Code scanning enabled
- ✅ Pre-commit hooks validate code quality
- ✅ No hardcoded secrets in repository

## Reporting a Vulnerability

### Integration Security Issues

If you discover a security vulnerability in **the integration itself** (services,
entities, controller logic):

1. **DO NOT** open a public issue
2. **Email:** Create a
   [security advisory](https://github.com/L3DigitalNet/HA-Light-Controller/security/advisories/new)
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**Response time:**

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Depends on severity (critical issues prioritized)

### Related Security Issues

If you discover a vulnerability in **Home Assistant core** or **related integrations**:

**Report to the appropriate repository**, not here. Each component has its own
maintainers and security process.

## Security Updates

### How We Handle Security Issues

1. **Assessment:** Evaluate severity and impact
2. **Fix:** Develop and test patch
3. **Disclosure:**
   - Critical: Immediate fix, then disclosure
   - High/Medium: Fix in next release, coordinated disclosure
   - Low: Fix in regular update cycle
4. **Notification:** Update CHANGELOG.md and create GitHub Security Advisory

### Severity Levels

**Critical:** Immediate action required

- Credential exposure
- Remote code execution
- Authentication bypass

**High:** Fix in next release (within 7 days)

- Privilege escalation
- Data leakage
- Injection vulnerabilities

**Medium:** Fix in upcoming release (within 30 days)

- Denial of service
- Information disclosure

**Low:** Fix in regular maintenance

- Security hardening
- Best practice improvements

## Security Best Practices for Integration Developers

### 1. Credential Management

```python
# ✅ CORRECT - Store in ConfigEntry
async def async_setup_entry(hass, entry):
    api_key = entry.data[CONF_API_KEY]
    client = MyApiClient(api_key)

# ❌ WRONG - Don't log credentials
_LOGGER.debug(f"Using API key: {api_key}")  # NEVER!
```

### 2. Input Validation

```python
# ✅ CORRECT - Validate user input
import voluptuous as vol

data_schema = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT): vol.All(int, vol.Range(min=1, max=65535)),
})
```

### 3. API Communication

```python
# ✅ CORRECT - Use HTTPS
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com/data") as resp:
        return await resp.json()

# ❌ WRONG - Never use HTTP for credentials
# http://api.example.com/login?password=...  # NEVER!
```

### 4. Error Handling

```python
# ✅ CORRECT - Don't expose internal details
except AuthenticationError as err:
    raise ConfigEntryAuthFailed("Invalid credentials") from err

# ❌ WRONG - Don't leak system info
except Exception as err:
    _LOGGER.error(f"Full system path: {err}")  # Don't expose paths!
```

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Home Assistant Security](https://www.home-assistant.io/docs/configuration/securing/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Acknowledgments

We appreciate responsible disclosure of security vulnerabilities. Contributors who
report valid security issues will be acknowledged in:

- Security advisories
- CHANGELOG.md
- GitHub Security Hall of Fame (if applicable)

## Questions?

For security-related questions (not vulnerabilities):

- [Discussions](https://github.com/L3DigitalNet/HA-Light-Controller/discussions)
- [Security Best Practices Guide](docs/SECURITY_BEST_PRACTICES.md)

For non-security bugs:

- [Issues](https://github.com/L3DigitalNet/HA-Light-Controller/issues)

---

**Last Updated:** 2026-02-07 **Security Contact:** Use GitHub Security Advisories
