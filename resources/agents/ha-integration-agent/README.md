# Home Assistant Integration Development Agent

A specialized AI agent designed to guide developers through creating high-quality Home Assistant integrations that meet or exceed the Integration Quality Scale standards.

## Table of Contents

- [Overview](#overview)
- [What This Agent Does](#what-this-agent-does)
- [Installation](#installation)
  - [Claude Code](#claude-code)
  - [VS Code with Codex](#vs-code-with-codex)
  - [VS Code with GitHub Copilot](#vs-code-with-github-copilot)
- [Usage](#usage)
  - [Using with Claude Code](#using-with-claude-code)
  - [Using with VS Code Extensions](#using-with-vs-code-extensions)
- [Agent Capabilities](#agent-capabilities)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Home Assistant Integration Development Agent is an expert system that embodies:
- Official Home Assistant developer documentation
- Integration Quality Scale requirements (Bronze → Platinum)
- Community best practices and patterns
- Python async programming expertise
- DataUpdateCoordinator pattern mastery

**Key Features:**
- ✅ Enforces Python 3.13+ requirements
- ✅ Mandates async-first architecture
- ✅ Requires config flows (no YAML-only)
- ✅ Promotes DataUpdateCoordinator pattern
- ✅ Provides community context awareness
- ✅ Guides toward quality tier progression

---

## What This Agent Does

### Phase 1: Discovery and Research
Before writing code, the agent:
1. Asks clarifying questions about your device/service
2. Simulates community forum research
3. Assesses existing solutions (core, HACS, PyPI)
4. Plans architecture (IoT class, platforms, auth strategy)

### Phase 2: Implementation Guidance
The agent provides:
1. DataUpdateCoordinator implementation
2. Config flow creation (mandatory)
3. Entity platform structure
4. Proper async patterns
5. Type-safe code examples

### Phase 3: Quality Assurance
The agent ensures:
1. Bronze tier minimum (config flow, tests, manifest)
2. Silver tier reliability (error handling, availability)
3. Gold tier completeness (async, type coverage, tests)
4. Platinum tier excellence (best practices, maintenance)

---

## Installation

### Claude Code

Claude Code uses agent definitions stored in `~/.claude/agents/`.

#### Quick Install

```bash
# Navigate to the agent directory
cd /home/chris/projects/ha-template/resources/agents/ha-integration-agent/

# Copy the agent to Claude's agent directory
cp ha_integration_agent_system_prompt.md ~/.claude/agents/ha-integration-agent.md

# Verify installation
ls -lh ~/.claude/agents/ha-integration-agent.md
```

#### Manual Install

1. **Locate the agent file:**
   ```bash
   /home/chris/projects/ha-template/resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md
   ```

2. **Create the Claude agents directory (if it doesn't exist):**
   ```bash
   mkdir -p ~/.claude/agents/
   ```

3. **Copy the system prompt:**
   ```bash
   cp ha_integration_agent_system_prompt.md ~/.claude/agents/ha-integration-agent.md
   ```

4. **Verify:**
   ```bash
   ls ~/.claude/agents/
   ```
   You should see `ha-integration-agent.md` listed.

---

### VS Code with Codex

GitHub Codex doesn't support custom agents directly, but you can use the agent's knowledge by including it as context.

#### Method 1: Workspace Context

1. **Create a `.codex/` directory in your project:**
   ```bash
   mkdir -p .codex/prompts/
   ```

2. **Copy the agent as a prompt template:**
   ```bash
   cp resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md \
      .codex/prompts/ha-integration-expert.md
   ```

3. **Reference in your code comments:**
   ```python
   # @codex-prompt: .codex/prompts/ha-integration-expert.md
   # Help me create a DataUpdateCoordinator for this integration
   ```

#### Method 2: Inline Context (Recommended)

Add this at the top of files you're working on:

```python
"""
Home Assistant Integration Development Guidelines:

This module follows HA Integration Quality Scale standards:
- Config flow UI setup (Bronze tier requirement)
- DataUpdateCoordinator pattern for data fetching
- Async-first architecture (no blocking I/O)
- Full type annotations (Python 3.13+)
- Proper error handling (UpdateFailed, ConfigEntryAuthFailed)

See: resources/agents/ha-integration-agent/ha_integration_agent_spec.md
"""
```

#### Method 3: Custom Instructions File

Create `.vscode/codex-instructions.md`:

```markdown
# Home Assistant Integration Development

When working with Home Assistant integrations in this workspace:

1. **Always use DataUpdateCoordinator** for polling integrations
2. **Config flows are mandatory** - no YAML-only configuration
3. **All I/O must be async** - use aiohttp, asyncio patterns
4. **Type hints required** - modern syntax (list[str] not List[str])
5. **Follow the manifest.json schema** - proper iot_class, integration_type

Reference: resources/agents/ha-integration-agent/
```

---

### VS Code with GitHub Copilot

GitHub Copilot uses context from your workspace and open files.

#### Method 1: Workspace Instructions (Recommended)

Create or update `.github/copilot-instructions.md` in your project root:

```markdown
# GitHub Copilot Instructions - Home Assistant Integration Development

## Context
This project develops Home Assistant custom integrations following the Integration Quality Scale.

## Requirements
- Python 3.13+ with modern type hints
- Async-first architecture (no blocking operations)
- DataUpdateCoordinator pattern for all polling integrations
- Mandatory config flows (no YAML configuration)

## Key Patterns

### DataUpdateCoordinator
Always use this pattern for polling:
```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

class MyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_data()
        except AuthError as err:
            raise ConfigEntryAuthFailed from err
        except ConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
```

### Config Flow
All integrations must have a config flow:
```python
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        # Implementation required
```

### Entity Base Class
Use CoordinatorEntity for automatic update handling:
```python
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class MyEntity(CoordinatorEntity[MyCoordinator]):
    _attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self._device_id}_{self._entity_type}"
```

## Quality Standards
- Bronze: Config flow + basic tests + manifest
- Silver: Error handling + availability management
- Gold: Full async + type coverage + comprehensive tests
- Platinum: All best practices + active maintenance

## References
- Spec: resources/agents/ha-integration-agent/ha_integration_agent_spec.md
- System Prompt: resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md
- HA Docs: https://developers.home-assistant.io/
```

#### Method 2: Open Agent Files

Keep the agent specification open in a tab while working. Copilot will use it as context:

1. **Open in VS Code:**
   ```bash
   code resources/agents/ha-integration-agent/ha_integration_agent_spec.md
   code resources/agents/ha-integration-agent/ha_integration_agent_system_prompt.md
   ```

2. **Keep these tabs open** while developing your integration

3. **Copilot will reference them** when generating code

#### Method 3: Comment-Based Context

Add structured comments in your code:

```python
"""
HA Integration Quality Requirements:
- [Bronze] Config flow UI setup
- [Bronze] Automated tests
- [Silver] Proper error handling
- [Gold] Full async codebase
- [Gold] Comprehensive type coverage

DataUpdateCoordinator pattern required for polling.
See: resources/agents/ha-integration-agent/ha_integration_agent_spec.md
"""

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# @copilot: Generate a DataUpdateCoordinator following HA best practices
class MyIntegrationCoordinator(DataUpdateCoordinator):
    # Copilot will suggest implementation based on context
```

---

## Usage

### Using with Claude Code

#### Method 1: Task Tool (Programmatic)

```python
from claude_code import Task

# Ask the agent for help
result = Task(
    subagent_type="ha-integration-agent",
    prompt="Help me create a config flow for a smart thermostat integration that uses OAuth2 authentication",
    description="Create OAuth2 config flow"
)
```

#### Method 2: Chat Interface

In Claude Code's chat interface:

```
@agent ha-integration-agent

I'm creating a Home Assistant integration for a smart thermostat. The device:
- Communicates via local HTTP REST API
- Requires username/password authentication
- Polls for temperature/humidity every 30 seconds
- Supports setting target temperature

Please guide me through creating this integration.
```

#### Method 3: Inline Questions

While editing code, invoke Claude and reference the agent:

```python
# Ask: How should I structure the coordinator for this integration?
# Context: Local polling device, 30s refresh interval
```

---

### Using with VS Code Extensions

#### With Codex

1. **Set up workspace context** (see installation above)

2. **Use inline comments:**
   ```python
   # Generate a DataUpdateCoordinator that polls a REST API every 30 seconds
   # Following HA Integration Quality Scale Bronze tier requirements
   ```

3. **Trigger Codex** with context-aware prompts

#### With GitHub Copilot

1. **Ensure `.github/copilot-instructions.md` exists** (see installation)

2. **Use descriptive function/class names:**
   ```python
   # Copilot understands HA patterns with good naming
   class SmartThermostatCoordinator(DataUpdateCoordinator):
       """Coordinator for Smart Thermostat data updates."""
       # Press Tab - Copilot suggests HA-compliant implementation
   ```

3. **Use comment-driven development:**
   ```python
   # Create a config flow step for OAuth2 authentication
   # Must follow HA config_entries.ConfigFlow pattern
   # Include error handling for invalid_auth and cannot_connect
   async def async_step_user(self, user_input):
       # Copilot generates implementation
   ```

4. **Ask Copilot Chat:**
   ```
   @workspace How should I implement a DataUpdateCoordinator for this integration following HA best practices?
   ```

---

## Agent Capabilities

### Code Generation

The agent can generate:
- ✅ Complete integration structure (manifest.json, __init__.py, const.py)
- ✅ DataUpdateCoordinator implementations
- ✅ Config flow with all steps (user, reauth, options)
- ✅ Entity platform files (sensor, binary_sensor, switch, etc.)
- ✅ Test files with proper mocking
- ✅ strings.json with translations

### Code Review

The agent can review:
- ✅ Compliance with Integration Quality Scale
- ✅ Async pattern correctness
- ✅ Error handling completeness
- ✅ Type annotation coverage
- ✅ Test adequacy

### Architecture Guidance

The agent provides:
- ✅ IoT class recommendations
- ✅ Platform selection (which entity types to create)
- ✅ Polling interval recommendations
- ✅ Authentication strategy
- ✅ Library separation guidance

---

## Examples

### Example 1: Creating a New Integration

**Prompt:**
```
I need to create a Home Assistant integration for a Philips Hue-like smart lighting system that:
- Uses a local REST API (http://bridge-ip/api/)
- Requires an API key for authentication
- Supports lights and sensors
- Should poll every 5 seconds

Guide me through the implementation.
```

**Agent Response:**
The agent will:
1. Ask clarifying questions about the API structure
2. Recommend IoT class: `local_polling`
3. Suggest platforms: `light`, `sensor`, `binary_sensor`
4. Provide DataUpdateCoordinator implementation
5. Create config flow for API key entry
6. Guide through entity creation
7. Ensure Bronze tier compliance minimum

---

### Example 2: Reviewing Existing Code

**Prompt:**
```
Review my config_flow.py for quality and best practices:

[paste your code]

What quality tier does this meet and what's needed for Gold tier?
```

**Agent Response:**
The agent will:
1. Analyze against Quality Scale requirements
2. Identify current tier (e.g., "meets Bronze, partial Silver")
3. List specific issues with code locations
4. Provide corrected code snippets
5. Create a roadmap to Gold tier

---

### Example 3: Debugging

**Prompt:**
```
My coordinator keeps marking entities unavailable even though the API is responding. Here's my code:

[paste coordinator code]

What's wrong?
```

**Agent Response:**
The agent will:
1. Identify the issue (e.g., incorrect exception handling)
2. Explain why it causes the problem
3. Provide corrected code
4. Suggest additional error handling improvements

---

## Best Practices

### 1. Start with Architecture

**Don't dive into code immediately.** Ask the agent:
```
Before I start coding, help me plan the architecture for [device/service].
What IoT class, platforms, and patterns should I use?
```

### 2. Aim for Bronze Minimum

**Every integration should meet Bronze tier:**
- Config flow UI setup
- Basic automated tests
- Proper manifest.json

Ask the agent:
```
What are the Bronze tier requirements for my integration type?
```

### 3. Use the Agent for Reviews

**Before submitting to HACS or core:**
```
Review my integration against the Quality Scale. What tier does it meet?
What changes are needed for [Silver/Gold/Platinum]?
```

### 4. Iterate with Feedback

**Don't try to be perfect first time:**
1. Get Bronze tier working
2. Ask agent for Silver tier improvements
3. Implement and test
4. Repeat for Gold tier

### 5. Learn the Patterns

**The agent teaches patterns:**
```
Explain why DataUpdateCoordinator is better than polling in __init__.py
```

Use this to understand WHY, not just WHAT.

---

## Troubleshooting

### Agent Not Responding in Claude Code

**Problem:** Agent doesn't seem to activate when called.

**Solution:**
1. Verify installation:
   ```bash
   ls -lh ~/.claude/agents/ha-integration-agent.md
   ```
2. Restart Claude Code
3. Use explicit agent invocation:
   ```python
   Task(subagent_type="ha-integration-agent", prompt="your question")
   ```

---

### Copilot Not Using Context

**Problem:** GitHub Copilot suggestions don't follow HA patterns.

**Solutions:**
1. Ensure `.github/copilot-instructions.md` exists in project root
2. Keep agent spec files open in tabs
3. Use more descriptive comments:
   ```python
   # DataUpdateCoordinator following HA Integration Quality Scale Bronze tier
   class MyCoordinator(DataUpdateCoordinator):
   ```

---

### Conflicting Patterns

**Problem:** Agent suggests different patterns than HA docs.

**Solution:**
The agent's knowledge cutoff is early 2025. For the latest patterns:
1. Check official docs: https://developers.home-assistant.io/
2. Ask the agent:
   ```
   Has the DataUpdateCoordinator pattern changed since early 2025?
   What should I verify in the latest docs?
   ```

---

### Quality Tier Confusion

**Problem:** Not clear what tier your integration meets.

**Solution:**
Ask the agent explicitly:
```
Review my integration files and tell me:
1. What tier does it currently meet?
2. What specific items are missing for the next tier?
3. Provide a checklist for Bronze/Silver/Gold/Platinum
```

---

## Files in This Directory

```
ha-integration-agent/
├── README.md                              # This file
├── ha_integration_agent_spec.md           # Comprehensive agent specification
├── ha_integration_agent_system_prompt.md  # Agent system prompt (install this)
├── manifest.json                          # Example manifest
├── __init__.py                            # Example integration entry point
├── const.py                               # Example constants
├── config_flow.py                         # Example config flow
├── coordinator.py                         # Example DataUpdateCoordinator
├── sensor.py                              # Example sensor platform
├── api.py                                 # Example API client
└── strings.json                           # Example translations
```

**Install:** `ha_integration_agent_system_prompt.md`
**Reference:** `ha_integration_agent_spec.md` (comprehensive patterns and examples)
**Examples:** Other `.py` and `.json` files (reference implementations)

---

## Resources

### Official Documentation
- [HA Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Creating Your First Integration](https://developers.home-assistant.io/docs/creating_component_index/)

### Community
- [HA Community Forums - Development](https://community.home-assistant.io/c/development/10)
- [HA Discord - Development Channel](https://discord.gg/home-assistant)

### Related Agents
- `ha-integration-dev.md` - Development assistance
- `ha-integration-debugger.md` - Debug coordinator/entity issues
- `ha-integration-reviewer.md` - Code review against Quality Scale

---

## License

This agent is part of the Home Assistant Integration Development Template.

## Contributing

To improve this agent:
1. Update `ha_integration_agent_system_prompt.md` with new patterns
2. Add examples to `ha_integration_agent_spec.md`
3. Test with real integration development
4. Submit improvements via PR

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-02 | 1.0.0 | Initial release |
| 2026-02 | 1.1.0 | Added VS Code extension instructions |

---

**Quick Start:** `cp ha_integration_agent_system_prompt.md ~/.claude/agents/ha-integration-agent.md`

**Support:** See [main template README](../../../README.md) for support resources.
