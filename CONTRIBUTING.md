# Contributing

## Core Rule

Do not modify `hermes-agent` source code for local behavior.

This repository exists so local extensions can live outside the upstream
Hermes Agent checkout. The operating rule is:

- Keep `/home/github/hermes-agent` aligned with upstream Hermes updates.
- Put local capabilities in this plugin pack.
- Prefer Hermes-native plugin APIs before considering any core change.
- If a capability cannot be implemented through existing plugin/tool hooks,
  document the limitation and consider an upstream issue or PR instead of
  maintaining a local fork.

## Extension Pattern

Add one plugin per directory:

```text
plugins/<plugin-name>/
  plugin.yaml
  __init__.py
```

The install script discovers any plugin directory containing both files.

## Endpoint Model

Treat `custom:<name>` entries as multi-capability endpoints, not as a single
image, text, video, or TTS backend.

Plugins should select the specific capability they need through their own
configuration. For example, the `openai-compatible` image plugin uses:

```yaml
image_gen:
  provider: openai-compatible
  openai_compatible:
    endpoint: custom:ttp
    model: gpt-image-2-medium
```

The same `custom:ttp` endpoint can still serve text models, image models, or
future capabilities independently.

## Validation

Run tests before publishing changes:

```bash
PYTHONPATH=/home/github/hermes-agent pytest -o addopts='' tests -q
```
