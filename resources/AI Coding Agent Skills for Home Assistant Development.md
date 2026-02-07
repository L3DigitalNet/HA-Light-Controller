Below is a set of **actionable Claude Code Agent Skills** based on the *Claude Agent Skills specification* — i.e., modular, reusable “skills” that teach Claude how to perform specific tasks automatically when relevant, encoded as SKILL.md-style capabilities. These skills are derived from the Home Assistant development skills we discussed earlier, and each is translated into a **Claude Skill intention** (with examples of when and how it would trigger) per the Claude Code documentation on Agent Skills.
Agent Skills are packaged as folders containing a `SKILL.md` with a **name**, **description**, **triggers/keywords**, and **instructions/examples** so Claude can load them dynamically in Claude Code or Claude.ai contexts when relevant. Skills are automatically invoked based on context in prompts without explicit user commands, or they can be invoked with `/skill-name` if needed. ([Claude][1])

---

## 📦 1) Home Assistant Architecture Skill

**Skill name:** `home-assistant-architecture`

**Description:**
Teach Claude to recognize and explain Home Assistant’s core architecture (event bus, state machine, services) and how integrations hook into it.

**When triggered:**
User queries about Home Assistant internal behavior, events, async loops, or integration patterns.

**Instruction snippets:**

* Provide concise definitions for event bus, state machine, and services.
* Include typical event patterns (e.g., `state_changed`).
* Explain how integrations register event listeners.

**Example usage:**

> *“Explain how Home Assistant events propagate for automation triggers.”*

---

## 📦 2) Async Python in Home Assistant Skill

**Skill name:** `ha-async-python`

**Description:**
Teach Claude to generate and explain asynchronous Python patterns used in Home Assistant integrations (`async_setup`, async services, non-blocking code).

**When triggered:**
Prompts mentioning async functions, event loops, or performance in Home Assistant.

**Instruction snippets:**

* Distinguish between `async_setup` vs synchronous setup.
* Provide examples using `hass.async_add_executor_job`.

**Example usage:**

> *“Generate async Setup code for a custom light platform.”*

---

## 📦 3) Python Integration Structure Skill

**Skill name:** `ha-python-integration-structure`

**Description:**
Guide Claude to scaffold Home Assistant custom components with correct file structure (manifest, platform files, requirements).

**When triggered:**
Requests for Home Assistant integration templates or component scaffolding.

**Instruction snippets:**

* Include manifest.json fields (domain, dependencies).
* Show typical file layout (`__init__.py`, `light.py`, etc.).
* Enforce Python library usage for device comms.

**Examples:**

> *“Scaffold a custom light integration with manifest and Python modules.”*

---

## 📦 4) YAML and Automation Schema Skill

**Skill name:** `ha-yaml-schema`

**Description:**
Train Claude to generate valid Home Assistant YAML (automations, scripts) with correct syntax and style.

**When triggered:**
Prompts involving YAML automations, scripts, or Blueprints.

**Instruction snippets:**

* Include rules: 2-space indentation, lowercase booleans.
* Provide common automation templates.

**Examples:**

> *“Write an automation YAML that turns lights on at sunset.”*

---

## 📦 5) Home Assistant Service Calls Skill

**Skill name:** `ha-service-calls`

**Description:**
Teach Claude to generate or explain service calls (`hass.services.async_call`) for controlling entities like lights/switches.

**When triggered:**
Queries about controlling entities, service invocation, or state updates.

**Instruction snippets:**

* Show examples for `light.turn_on`, `light.turn_off`.
* Include parameters (brightness, color).

**Examples:**

> *“Write Python code to turn on a light with brightness 200.”*

---

## 📦 6) Domain Knowledge: Lights & Switches Skill

**Skill name:** `ha-domain-light-switch`

**Description:**
Embed knowledge about Home Assistant light and switch domains so Claude understands relevant entity attributes and differences.

**When triggered:**
Prompts concerning behavior, capabilities, or attributes of lights/switches.

**Instruction snippets:**

* Explain light domain fields (brightness, color, effects).
* Clarify switch domain attributes (binary on/off).

**Examples:**

> *“When should I use a light service vs switch service?”*

---

## 📦 7) UI Config Flow Skill

**Skill name:** `ha-config-flow-ui`

**Description:**
Train Claude to write and explain configuration flow Python code (`config_flow.py`, `options_flow.py`) for Home Assistant integrations with UI setup.

**When triggered:**
Prompts referencing UI set up without YAML.

**Instruction snippets:**

* Step-by-step patterns for `ConfigFlow`.
* User input validation using `voluptuous`.

**Examples:**

> *“Generate a config flow for a light integration with username/password.”*

---

## 📦 8) Developer Tools & Debugging Skill

**Skill name:** `ha-debugging-devtools`

**Description:**
Equip Claude to suggest debugging steps, logs, developer tools checks (Dev Tools, logs, automation traces) specific to Home Assistant.

**When triggered:**
Requests about errors, debugging failure, or understanding logs.

**Instruction snippets:**

* How to enable debug logging for components.
* How to view logs via Home Assistant UI or CLI.

**Examples:**

> *“How do I track down a failing automation?”*

---

## 📦 9) Testing Home Assistant Code Skill

**Skill name:** `ha-testing-automation`

**Description:**
Show Claude how to generate tests for Home Assistant integrations using `pytest` and the `hass` fixture.

**When triggered:**
Prompts asking for test code or testing guidance.

**Instruction snippets:**

* Example test using Home Assistant `hass` fixture.
* Simulating state changes and service calls.

**Examples:**

> *“Write a pytest case for light integration turning off automatically.”*

---

## 🧠 How Skills Are Structured (Claude Agent Specs)

Each Skill should include (in `SKILL.md`):

**Frontmatter**

```md
---
name: ha-service-calls
description: Teach Claude how to generate and explain Home Assistant service call code specifically for entity control tasks.
---
```

**Body Instructions**

```md
# Overview
When prompted about controlling Home Assistant entities, include callable service call examples such as:

- Python: `await hass.services.async_call("light", "turn_on", {"entity_id": "light.foo"})`
- YAML: automation/service example

# Examples
- "Turn on light X at 7pm"
- "Set brightness to 180 using service data"
```

Skills can also include templates, code snippets, sample YAML, and progressive examples. Claude loads minimal relevant content automatically in context based on the prompt. ([Claude][1])

---

## 🔄 Invocation & Deployment

* **Automatic invocation:** Claude will match user queries to Skills based on keywords and context (e.g., “Home Assistant async”, “service call”, “config flow”). ([Claude][1])
* **Explicit invocation:** Users can trigger with `/ha-service-calls` if integrated into Claude Code. ([Claude Code][2])
* **Placement:** For Claude Code CLI or local installs, place Skills under `.claude/skills/skill-name/SKILL.md`. ([Claude][1])

Each of the above Skills encodes **procedural knowledge** and **reusable templates/resources** so Claude can assist reliably, avoiding repetitive context building while generating code tailored to Home Assistant Python/YAML development. ([Claude][3])

---
