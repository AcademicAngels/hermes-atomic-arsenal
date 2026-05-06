# Review Release Loop

## Purpose

Use this loop when a Hermes reviewer profile validates a branch, release
candidate, or completed Kanban task chain.

## Inputs

- Kanban task summaries and run metadata
- Current git branch and diff
- Test, lint, build, or deployment evidence
- Deployment facts from the relevant runbook

## Preflight

Run or inspect:

```bash
git status --short --branch
git diff --stat
```

Read deployment facts before commenting on runtime behavior:

```bash
sed -n '1,220p' /home/github/hermes-agent/docs/deploy/agent-first.md
```

## Iteration

Review in this order:

1. Correctness and behavioral regressions.
2. Safety, secrets, destructive operations, and deployment risk.
3. Test or verification gaps.
4. Documentation accuracy.
5. Scope creep and upstream compatibility.

Findings must include file paths, commands, or concrete evidence. Do not block
on style-only issues unless they cause maintainability risk.

## Verification

Run the highest-signal verification that is feasible in the current task:

```bash
pytest -q
```

If full tests are too expensive or unavailable, run the targeted checks listed
by the worker and record the residual risk.

## Completion Criteria

Set `loop_status` to:

- `complete` when the release/task is acceptable and no review follow-up is
  needed
- `continue` when the worker should make specific fixes
- `blocked` when required evidence or environment access is unavailable

## Handoff

Write:

```yaml
summary: <approval, requested changes, or block reason>
loop_ref: loops/review-release
loop_status: complete | continue | blocked
artifacts:
  - <diff or files reviewed>
  - <verification command and result>
blocked_reason: <only if blocked>
next_step: <only if continue>
```
