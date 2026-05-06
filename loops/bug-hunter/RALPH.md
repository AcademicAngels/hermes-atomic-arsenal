# Bug Hunter Loop

## Purpose

Use this loop for a bounded bug investigation or fix in a Hermes team-mode
Kanban task.

## Inputs

- Kanban task title and body
- Parent task summaries and reviewer comments
- Current git diff
- Relevant logs, failing commands, or reproduction steps

## Preflight

Run or inspect:

```bash
git status --short --branch
rg -n "<error text or failing symbol>" .
```

If the task names a specific command that fails, run that command before
editing. Capture the exact failure in the handoff.

## Iteration

Do one bounded step:

1. Identify the smallest plausible root cause from the evidence.
2. Inspect the directly related files.
3. Make the smallest code, config, or documentation change that addresses the
   root cause.
4. Avoid unrelated refactors.
5. Preserve user or teammate changes already present in the worktree.

## Verification

Run the narrowest command that proves the fix or investigation result. Prefer:

```bash
pytest -q <relevant-test-path>
```

If no automated test exists, run the original failing command or a focused
manual check and record the limitation.

## Completion Criteria

Set `loop_status` to:

- `continue` when the root cause is clearer but another edit or test is needed
- `needs_review` when the fix is implemented and verification evidence exists
- `blocked` when missing access, missing data, or unsafe side effects prevent
  progress
- `complete` only for tasks that explicitly do not require review

## Handoff

Write:

```yaml
summary: <root cause and result>
loop_ref: loops/bug-hunter
loop_status: continue | needs_review | blocked | complete
artifacts:
  - <files changed>
  - <verification command and result>
blocked_reason: <only if blocked>
next_step: <only if continue or needs_review>
```
