# Documentation Index

This directory contains comprehensive implementation guides for HA Light Controller
development.

## Quick Links

| Guide                                                 | Purpose                                     | Audience              |
| ----------------------------------------------------- | ------------------------------------------- | --------------------- |
| [Quality Checklist](QUALITY_CHECKLIST.md)             | Track progress toward Bronze→Platinum tiers | All developers        |
| [HACS Integration](HACS_INTEGRATION.md)               | Publish integration to HACS                 | Distribution planning |
| [Security Best Practices](SECURITY_BEST_PRACTICES.md) | Secure credential and API handling          | All developers        |
| [Migration Guide](MIGRATION_GUIDE.md)                 | Config entry version migrations             | Maintenance           |
| [Performance](PERFORMANCE.md)                         | Optimization and efficiency tips            | Intermediate+         |
| [Localization](LOCALIZATION.md)                       | Multi-language support                      | I18n implementation   |

## Documentation Organization

### Essential Reading

**For New Contributors:**

1. Start with [../README.md](../README.md) for project overview
2. Review [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md) to understand quality tiers
3. Read [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) before implementing
   auth

**For Publishing:**

1. Achieve at least Bronze tier (see [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md))
2. Follow [HACS_INTEGRATION.md](HACS_INTEGRATION.md) for HACS submission
3. Use [../CHANGELOG.md](../CHANGELOG.md) to document releases

**For Maintenance:**

1. Reference [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) when changing config entry
   structure
2. Use [PERFORMANCE.md](PERFORMANCE.md) to optimize performance
3. Implement [LOCALIZATION.md](LOCALIZATION.md) for international users

### Additional Resources

- **[../CLAUDE.md](../CLAUDE.md)** - AI assistant instructions and mandatory patterns
- **[../REFERENCE_GUIDE.md](../REFERENCE_GUIDE.md)** - Comprehensive technical reference
- **[../resources/ha-dev-environment-requirements.md](../resources/ha-dev-environment-requirements.md)** -
  Environment setup
- **[../.github/AUTOMATION_GUIDE.md](../.github/AUTOMATION_GUIDE.md)** - CI/CD and
  automation

## How to Use This Documentation

### Development Workflow

```bash
# 1. Initial setup
source venv/bin/activate
python scripts/verify_environment.py

# 2. Track progress
# Open docs/QUALITY_CHECKLIST.md and check off items as you implement them

# 3. Implement securely
# Reference docs/SECURITY_BEST_PRACTICES.md while coding

# 4. Optimize
# Use docs/PERFORMANCE.md to ensure efficient light control

# 5. Localize (optional)
# Follow docs/LOCALIZATION.md to add translations

# 6. Migrate (when needed)
# Use docs/MIGRATION_GUIDE.md for config entry updates

# 7. Publish
# Follow docs/HACS_INTEGRATION.md for HACS submission
```

### Quality Tier Progression

Track progress toward Home Assistant's Integration Quality Scale tiers:

1. **Bronze (Minimum)** - Start here
   - Config flow UI setup
   - Automated tests
   - Basic coding standards
   - See [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md) for complete list

2. **Silver (Reliability)** - Recommended minimum
   - Error handling
   - Entity availability
   - Troubleshooting docs
   - User-friendly config flow

3. **Gold (Feature Complete)** - Professional quality
   - Full async codebase
   - ≥90% test coverage
   - Complete type annotations
   - Efficient data handling

4. **Platinum (Excellence)** - Core integration quality
   - All best practices
   - Clear documentation
   - Optimal performance
   - Active maintenance

## Common Questions

**Q: Where do I start?** A: Read [../README.md](../README.md) first, then open
[QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md) to see what you need to implement.

**Q: How do I distribute the integration?** A: Follow
[HACS_INTEGRATION.md](HACS_INTEGRATION.md) after achieving Bronze tier minimum.

**Q: The integration is slow. How do I optimize it?** A: Review
[PERFORMANCE.md](PERFORMANCE.md) for optimization strategies.

**Q: How do I handle credentials securely?** A: Read
[SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md) for authentication patterns.

**Q: I need to change the config entry structure. How?** A: Use
[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) to implement async_migrate_entry().

**Q: How do I add translations?** A: Follow [LOCALIZATION.md](LOCALIZATION.md) for
strings.json and translations/ setup.

## Contributing to Documentation

Found an issue or want to improve these guides?

1. File an issue at the repository's issue tracker
2. Submit a pull request with improvements
3. Include examples and code snippets where applicable
4. Follow the existing structure and tone

## Related Documentation

- **Integration Code**:
  [../custom_components/ha_light_controller/](../custom_components/ha_light_controller/)
- **Test Suite**: [../tests/](../tests/)
- **Skills & Agents**: [../resources/](../resources/)
- **GitHub Workflows**: [../.github/workflows/](../.github/workflows/)

---

**Need help?** Join the [Home Assistant Community](https://community.home-assistant.io/)
or check the [HA Developer Docs](https://developers.home-assistant.io/).
