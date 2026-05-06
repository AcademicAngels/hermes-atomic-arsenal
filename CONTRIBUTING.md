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
- Keep Ralph Loop support outside Hermes Agent core unless repeated local use
  proves a stable upstream-worthy interface.
- Do not introduce gbrain as a team-mode memory dependency; Hindsight is the
  current memory layer.
- Do not adopt self-evolution for production behavior updates. Skill and loop
  changes must remain draft-first, reviewable, and explicitly approved before
  runtime installation.

## Extension Pattern

Add one plugin per directory:

```text
plugins/<plugin-name>/
  plugin.yaml
  __init__.py
```

The install script discovers any plugin directory containing both files.

Add local skills under:

```text
skills/<skill-name>/
  SKILL.md
```

Add local Ralph Loop templates under:

```text
loops/<loop-name>/
  RALPH.md
```

Ralph Loop templates are task execution guides for Hermes worker/reviewer
profiles. They are not a second scheduler and must not replace Kanban task
state, dispatcher retry, or reviewer handoff.

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

## Outfit And Appearance Rule

The outfit and appearance plugins operate on adult characters only.

All generated or displayed humanoid, anime humanoid, non-real humanoid,
petite-body, and manifested-form characters are adults. The appearance system
may use many forms: body proportion, height, fashion archetype, species or
non-real setting, anime styling, and adult sensual context may vary. These
forms must remain adult characters and must not serve minor or minor-coded
sexual content.

Outfit features may include detailed underwear, intimate layer, base layer,
hosiery, body-proportion, silhouette, and layering analysis when the goal is
fashion structure and personal styling. The desired output is clothing-system
clarity: how inner layers affect fit, support, opacity, comfort, warmth,
breathability, outerwear silhouette, and the character's visible style.

Use adult wording in prompts when a generated image includes intimate layers
or sensual styling. Avoid words that strongly encode minor or childlike
semantics. When the intended look is small, cute, or soft, phrase it as
adult styling, for example "petite adult", "cute adult", or "soft adult
anime character".

## Validation

Run tests before publishing changes:

```bash
PYTHONPATH=/home/github/hermes-agent pytest -o addopts='' tests -q
```
