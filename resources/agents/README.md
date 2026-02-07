# Home Assistant Integration Development Agents for Claude Code

A suite of specialized Claude Code subagents for developing high-quality Home Assistant integrations.

## Included Agents

| Agent | Purpose |
|-------|---------|
| `ha-integration-dev` | Main development agent - guides you through creating integrations with proper patterns |
| `ha-integration-reviewer` | Code reviewer - checks your code against the Integration Quality Scale |
| `ha-integration-debugger` | Debugging specialist - helps diagnose and fix common integration issues |

## Installation

### Option 1: Project-Level Installation (Recommended)

Install the agents in a specific project where you're developing Home Assistant integrations:

```bash
# Navigate to your project directory
cd /path/to/your/ha-integration-project

# Create the agents directory
mkdir -p .claude/agents

# Copy the agent files
cp ha-integration-dev.md .claude/agents/
cp ha-integration-reviewer.md .claude/agents/
cp ha-integration-debugger.md .claude/agents/
```

### Option 2: User-Level Installation

Install the agents globally so they're available in all your projects:

```bash
# Create the user agents directory
mkdir -p ~/.claude/agents

# Copy the agent files
cp ha-integration-dev.md ~/.claude/agents/
cp ha-integration-reviewer.md ~/.claude/agents/
cp ha-integration-debugger.md ~/.claude/agents/
```

### Option 3: One-Line Installation

```bash
# Project-level
mkdir -p .claude/agents && cp *.md .claude/agents/

# User-level
mkdir -p ~/.claude/agents && cp *.md ~/.claude/agents/
```

## Usage

### Automatic Delegation

Claude Code will automatically delegate to these agents when it detects relevant tasks. The agents are configured with `PROACTIVELY` and `MUST BE USED` triggers for:

- Creating Home Assistant integrations
- Reviewing integration code
- Debugging integration issues

### Explicit Invocation

You can also explicitly request a specific agent:

```
> Use the ha-integration-dev agent to help me create a new integration for my smart thermostat

> Have the ha-integration-reviewer agent check my integration code

> Ask the ha-integration-debugger agent to investigate why my entities aren't appearing
```

### Managing Agents

Use the `/agents` command in Claude Code to:
- View all available agents
- Edit agent configurations
- Adjust tool permissions
- Create new agents

```
/agents
```

## Agent Capabilities

### ha-integration-dev

**Tools:** Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch

This is your primary development companion. It will:
- Research the Home Assistant community forums for relevant context
- Guide you through proper architecture decisions
- Generate complete, working code with full explanations
- Enforce best practices like DataUpdateCoordinator and config flows
- Push you toward Silver/Gold quality tier standards

**Example prompts:**
```
> Create a Home Assistant integration for a device that uses a REST API with OAuth2 authentication

> Help me add an options flow to configure the polling interval

> How do I implement device discovery using mDNS?
```

### ha-integration-reviewer

**Tools:** Read, Grep, Glob, Bash (read-only operations)

Use after writing code to get a quality assessment. It will:
- Run linting and type checking
- Review against the Integration Quality Scale
- Identify critical issues, warnings, and suggestions
- Provide specific code fixes

**Example prompts:**
```
> Review my integration code before I submit the PR

> Check if my integration meets Silver tier requirements

> What do I need to fix for core submission?
```

### ha-integration-debugger

**Tools:** Read, Edit, Bash, Grep, Glob

Use when things aren't working. It will:
- Analyze error messages and stack traces
- Identify common failure patterns
- Provide targeted fixes with explanations
- Suggest verification steps

**Example prompts:**
```
> My entities are showing as unavailable - help me debug

> The config flow throws an "unexpected exception" - what's wrong?

> Why isn't my coordinator updating data?
```

## Best Practices

1. **Start with the dev agent** to set up your integration structure correctly from the beginning

2. **Use the reviewer** before committing or submitting PRs to catch issues early

3. **Chain agents** for complex workflows:
   ```
   > Use ha-integration-dev to add a new sensor platform, then have ha-integration-reviewer check the code
   ```

4. **Resume agents** for long-running tasks:
   ```
   > Resume agent abc123 and continue implementing the binary sensor platform
   ```

## Customization

Feel free to edit the agent files to:
- Adjust tool permissions
- Modify the system prompts
- Add project-specific instructions
- Change model selection (sonnet/opus/haiku)

Use `/agents` in Claude Code for an interactive editing experience.

## Requirements

- Claude Code (latest version)
- For development: Python 3.12+ and a Home Assistant dev environment

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
- [Integration Blueprint Template](https://github.com/ludeeus/integration_blueprint)
- [Community Forum - Development](https://community.home-assistant.io/c/development/10)
