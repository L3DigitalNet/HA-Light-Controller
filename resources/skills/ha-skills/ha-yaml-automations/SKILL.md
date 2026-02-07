---
name: ha-yaml-automations
description: Generate valid Home Assistant YAML automations, scripts, and blueprints. Use when the user asks to write an automation, create a script, build a blueprint, or needs help with Home Assistant YAML syntax. Triggers on "automation", "script", "blueprint", "trigger", "condition", "action" in a Home Assistant context.
---

# Home Assistant YAML Automations and Scripts

## YAML Style Rules

Home Assistant enforces specific YAML conventions. Always follow these:

- **2-space indentation** (never tabs)
- **Lowercase booleans**: `true` / `false` (not `True` / `False` / `yes` / `no`)
- **Quoted strings** only when needed (colons, special characters)
- **No trailing whitespace**
- **Entity IDs**: always `domain.entity_name` format (lowercase, underscores)

## Automation Template

```yaml
automation:
  - id: "unique_automation_id"
    alias: "Descriptive Name"
    description: "What this automation does and why"
    mode: single  # single | restart | queued | parallel
    trigger:
      - trigger: state
        entity_id: binary_sensor.front_door
        to: "on"
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - action: light.turn_on
        target:
          entity_id: light.hallway
        data:
          brightness_pct: 100
```

## Common Trigger Types

```yaml
# State trigger
- trigger: state
  entity_id: sensor.temperature
  above: 25

# Time trigger
- trigger: time
  at: "07:30:00"

# Sun trigger
- trigger: sun
  event: sunset
  offset: "-00:30:00"

# Template trigger
- trigger: template
  value_template: "{{ states('sensor.power') | float > 1000 }}"

# MQTT trigger
- trigger: mqtt
  topic: "home/sensor/motion"
  payload: "on"

# Webhook trigger
- trigger: webhook
  webhook_id: "my_unique_webhook_id"
  allowed_methods:
    - POST

# Device trigger
- trigger: device
  device_id: abc123
  domain: zha
  type: remote_button_short_press
```

## Common Condition Types

```yaml
# State condition
- condition: state
  entity_id: alarm_control_panel.home
  state: "armed_away"

# Numeric state condition
- condition: numeric_state
  entity_id: sensor.temperature
  above: 20
  below: 30

# Time condition
- condition: time
  after: "08:00:00"
  before: "23:00:00"
  weekday:
    - mon
    - tue
    - wed
    - thu
    - fri

# Template condition
- condition: template
  value_template: "{{ is_state('person.john', 'home') }}"

# AND / OR grouping
- condition: and
  conditions:
    - condition: state
      entity_id: input_boolean.guest_mode
      state: "off"
    - condition: state
      entity_id: binary_sensor.motion
      state: "on"
```

## Common Action Types

```yaml
# Service call
- action: light.turn_on
  target:
    entity_id: light.living_room
  data:
    brightness_pct: 80
    color_temp_kelvin: 3000

# Delay
- delay:
    seconds: 30

# Wait for trigger
- wait_for_trigger:
    - trigger: state
      entity_id: binary_sensor.motion
      to: "off"
  timeout:
    minutes: 5
  continue_on_timeout: true

# Choose (if/else)
- choose:
    - conditions:
        - condition: state
          entity_id: input_select.mode
          state: "away"
      sequence:
        - action: climate.set_temperature
          target:
            entity_id: climate.thermostat
          data:
            temperature: 18
    - conditions:
        - condition: state
          entity_id: input_select.mode
          state: "home"
      sequence:
        - action: climate.set_temperature
          target:
            entity_id: climate.thermostat
          data:
            temperature: 22
  default:
    - action: notify.mobile_app
      data:
        message: "Unknown mode selected"

# Repeat
- repeat:
    count: 3
    sequence:
      - action: light.toggle
        target:
          entity_id: light.alert
      - delay:
          seconds: 1
```

## Script Template

```yaml
script:
  morning_routine:
    alias: "Morning Routine"
    description: "Runs the morning routine sequence"
    mode: single
    fields:
      brightness:
        description: "Light brightness level"
        example: 80
        default: 100
        selector:
          number:
            min: 0
            max: 100
    sequence:
      - action: light.turn_on
        target:
          area_id: kitchen
        data:
          brightness_pct: "{{ brightness }}"
      - action: media_player.play_media
        target:
          entity_id: media_player.kitchen_speaker
        data:
          media_content_id: "https://radio.example.com/stream"
          media_content_type: "music"
```

## Blueprint Template

```yaml
blueprint:
  name: "Motion-Activated Light"
  description: "Turn on a light when motion is detected, turn off after delay"
  domain: automation
  input:
    motion_entity:
      name: "Motion Sensor"
      selector:
        entity:
          filter:
            domain: binary_sensor
            device_class: motion
    light_target:
      name: "Light"
      selector:
        target:
          entity:
            domain: light
    no_motion_wait:
      name: "Wait time"
      description: "Time to leave the light on after last motion"
      default: 120
      selector:
        number:
          min: 0
          max: 3600
          unit_of_measurement: seconds

trigger:
  - trigger: state
    entity_id: !input motion_entity
    to: "on"

action:
  - action: light.turn_on
    target: !input light_target
  - wait_for_trigger:
      - trigger: state
        entity_id: !input motion_entity
        to: "off"
  - delay:
      seconds: !input no_motion_wait
  - action: light.turn_off
    target: !input light_target

mode: restart
```

## Key Rules

1. Use `action:` not `service:` (renamed in recent HA versions)
2. Use `trigger:` as the trigger type key (e.g., `trigger: state` not `platform: state`)
3. Always include `alias` and `description` for readability
4. Use `target:` with `entity_id`, `area_id`, or `device_id` for targeting
5. Template values use Jinja2 syntax: `"{{ states('sensor.x') }}"`
6. Set appropriate `mode` to handle overlapping triggers
