# Docs Maintainer Loop

## Purpose

Use this loop when updating local Hermes deployment, architecture, or team-mode
documentation.

## Inputs

- User request and accepted architecture constraints
- Current docs and related specs
- Current git diff
- Relevant runtime facts if the doc describes deployment behavior

## Preflight

Run or inspect:

```bash
git status --short --branch
rg -n "<topic keyword>" docs README.md CONTRIBUTING.md
```

For Hermes Agent deployment docs, treat this runbook as the deployment fact
source:

```text
/home/github/hermes-agent/docs/deploy/agent-first.md
```

## Iteration

Do one bounded documentation step:

1. Add the accepted decision where future workers will look first.
2. Separate architecture decisions from implementation conveniences.
3. Mark non-goals and source-impact boundaries explicitly.
4. Avoid documenting secrets or environment values that should stay local.
5. Keep wording compatible with upstream-following local extension strategy.

## Verification

Run:

```bash
git diff -- <changed-doc-path>
rg -n "TODO|TBD|PLACEHOLDER" <changed-doc-path>
```

If the doc contains commands, inspect them for path accuracy.

## Completion Criteria

Set `loop_status` to:

- `needs_review` when the doc update is ready for user or reviewer review
- `continue` when more sections need the same accepted decision
- `blocked` when the source of truth is missing or contradictory
- `complete` only for small doc-only tasks that do not require review

## Handoff

Write:

```yaml
summary: <decision documented and where>
loop_ref: loops/docs-maintainer
loop_status: needs_review | continue | blocked | complete
artifacts:
  - <doc paths changed>
  - <verification command and result>
blocked_reason: <only if blocked>
next_step: <only if continue or needs_review>
```
