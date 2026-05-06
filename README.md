# Hermes Atomic Arsenal

Hermes 原子武器库。

Local plugin pack for Hermes Agent extensions.

This repository is a collection of Hermes-native plugins. It is structured as a
plugin pack because Hermes currently installs one plugin per Git repository via
`hermes plugins install`, while this project is meant to carry multiple local
extensions over time.

## Project Principle

This project keeps local extensions outside the `hermes-agent` source tree so
Hermes can continue to follow upstream updates cleanly. Add local capabilities
here as plugins; do not patch `hermes-agent` for site-specific behavior.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development rule.

## Plugins

- `openai-compatible`: image generation backend that uses an endpoint from
  Hermes `custom_providers`, such as `custom:ttp`, through an OpenAI-compatible
  Images API.

## Skills

- `team-ralph-loop`: reads local Ralph Loop templates for Hermes team-mode
  Kanban tasks without requiring Hermes core changes.

## Ralph Loop Templates

Ralph Loop templates live under `loops/<name>/RALPH.md`. They are local,
reviewable task-loop instructions for worker/reviewer profiles. They do not
replace Hermes Kanban, Profiles, or Dispatcher, and they are not native Hermes
runtime dependencies.

Initial templates:

- `bug-hunter`: bounded bug investigation and fix loop.
- `review-release`: reviewer/release validation loop.
- `docs-maintainer`: documentation decision and runbook maintenance loop.

## Install

From this repository:

```bash
python3 scripts/install.py --home /home/hermes_data --force --enable
```

Install only one plugin:

```bash
python3 scripts/install.py openai-compatible --home /home/hermes_data --force --enable
```

Install skills and Ralph Loop templates:

```bash
python3 scripts/install.py --home /home/hermes_data --force --skip-plugins --skills --loops
```

Install everything carried by this repository:

```bash
python3 scripts/install.py --home /home/hermes_data --force --enable --all-assets
```

Then configure Hermes:

```bash
HERMES_HOME=/home/hermes_data hermes config set image_gen.provider openai-compatible
HERMES_HOME=/home/hermes_data hermes config set image_gen.openai_compatible.endpoint custom:ttp
HERMES_HOME=/home/hermes_data hermes config set image_gen.openai_compatible.model gpt-image-2-medium
```

Restart the Hermes gateway/native service after installing or updating plugins.

## Configuration Model

`custom:ttp` remains a multi-capability endpoint. The plugin only uses the image
generation capability selected under `image_gen.openai_compatible`.

Example:

```yaml
custom_providers:
  - name: ttp
    base_url: https://api.husanai.com/v1
    api_key: ...
    model: gpt-5.5

image_gen:
  provider: openai-compatible
  model: gpt-image-2-medium
  openai_compatible:
    endpoint: custom:ttp
    model: gpt-image-2-medium
```

## Test

Run tests from the repository root:

```bash
PYTHONPATH=/home/github/hermes-agent pytest -o addopts='' tests -q
```

## Add A Plugin

Add a new directory under `plugins/<plugin-name>/` with:

- `plugin.yaml`
- `__init__.py`

The install script automatically discovers plugin directories with both files.

## Add A Skill

Add a new directory under `skills/<skill-name>/` with:

- `SKILL.md`

## Add A Ralph Loop

Add a new directory under `loops/<loop-name>/` with:

- `RALPH.md`

Ralph Loop templates should be task-specific and concise. Keep coordination
state in Hermes Kanban; keep the template focused on iteration steps,
verification commands, completion criteria, and handoff fields.
