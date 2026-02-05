# Home Assistant Development Skills for Claude Code

A comprehensive suite of Agent Skills that equip Claude Code with deep expertise in Home Assistant integration development. These skills are automatically invoked when Claude detects relevant context in your prompts, giving you on-demand access to HA development best practices without repetitive prompting.

## What's Included

This suite contains 11 modular skills covering the full integration development lifecycle, from architecture understanding through quality review. Each skill is a self-contained folder with a `SKILL.md` file and optional supporting reference material.

### Core Architecture & Patterns

| Skill | Slash Command | Description |
|---|---|---|
| **ha-architecture** | `/ha-architecture` | Core HA internals: event bus, state machine, service registry, entity lifecycle, device/entity registries |
| **ha-async-patterns** | `/ha-async-patterns` | Async Python patterns: executor jobs, callbacks vs coroutines, timeouts, task management |
| **ha-coordinator** | `/ha-coordinator` | DataUpdateCoordinator implementation: `_async_setup`, `_async_update_data`, error handling, `always_update` |

### Integration Development

| Skill | Slash Command | Description |
|---|---|---|
| **ha-integration-scaffold** | `/ha-integration-scaffold` | Scaffold a new integration with correct file structure, manifest.json, and boilerplate |
| **ha-config-flow** | `/ha-config-flow` | Config flow, options flow, reauth flow, strings.json, and discovery methods |
| **ha-entity-platforms** | `/ha-entity-platforms` | Entity platform patterns (sensor, binary_sensor, switch, light, cover, climate, etc.) with EntityDescription |
| **ha-service-calls** | `/ha-service-calls` | Service call patterns in Python and YAML, service registration, entity services |

### Automation & Configuration

| Skill | Slash Command | Description |
|---|---|---|
| **ha-yaml-automations** | `/ha-yaml-automations` | YAML automations, scripts, and blueprints with correct syntax and modern patterns |

### Quality & Testing

| Skill | Slash Command | Description |
|---|---|---|
| **ha-testing** | `/ha-testing` | pytest patterns, hass fixture, config flow tests, setup/unload tests, mocking |
| **ha-debugging** | `/ha-debugging` | Diagnostic workflows, common error patterns, log analysis, troubleshooting checklist |
| **ha-quality-review** | `/ha-quality-review` | Integration Quality Scale review (Bronze through Platinum tier assessment) |

## Installation

### Option A: Project-Level (Recommended for HA Development Projects)

Place the skills in your project so they're available when working in that directory and shareable with your team via git.

```bash
# From the root of your HA integration project
cp -r .claude/ /path/to/your/project/.claude/

# Commit to share with your team
git add .claude/skills/
git commit -m "Add Home Assistant development skills for Claude Code"
```

### Option B: User-Level (Available Everywhere)

Install the skills globally so Claude Code can use them in any project.

```bash
# Copy skills to your user directory
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

### Option C: Quick Install Script

```bash
# Project-level
./install.sh project

# User-level
./install.sh user
```

## How Skills Work

Skills are **model-invoked** — Claude autonomously decides when to load them based on your prompt and each skill's description. You do not need to do anything special to trigger them.

**Automatic invocation examples:**

| You say... | Claude loads... |
|---|---|
| "Create a new integration for my smart thermostat" | `ha-integration-scaffold`, `ha-config-flow`, `ha-coordinator` |
| "Why are my entities showing unavailable?" | `ha-debugging`, `ha-coordinator` |
| "Write a test for my config flow" | `ha-testing` |
| "How does the event bus work in HA?" | `ha-architecture` |
| "Write an automation that turns on lights at sunset" | `ha-yaml-automations` |

**Explicit invocation:** You can also trigger any skill directly by typing its slash command (e.g., `/ha-quality-review`) in Claude Code.

## Skill Dependencies

Some skills reference others for deeper guidance. When a skill mentions "see the `ha-coordinator` skill," Claude will load that skill's content as needed. The `ha-quality-review` skill in particular acts as a hub, routing you to the appropriate skill for each issue it finds.

## Supporting Files

Several skills include reference files that Claude loads on demand (progressive disclosure) to keep context efficient:

- `ha-entity-platforms/reference/device-classes.md` — Complete device class reference for sensors, binary sensors, covers, switches, and buttons
- `ha-config-flow/reference/discovery-methods.md` — Zeroconf, SSDP, DHCP, USB, and Bluetooth discovery implementation patterns

## Customization

Edit any `SKILL.md` to add project-specific conventions. For example, you might add your team's preferred polling interval, required entity platforms, or mandatory test coverage thresholds to the relevant skill.

Skills with `disable-model-invocation: true` (like `ha-quality-review`) are only invoked when you explicitly call them with the slash command. This prevents heavyweight review workflows from triggering on casual mentions of "quality" or "review."

## Requirements

- Claude Code 1.0 or later
- For development: Python 3.13+ and a Home Assistant development environment

## Version History

- v1.0.0 (2026-02-05): Initial release with 11 skills covering full HA development lifecycle
