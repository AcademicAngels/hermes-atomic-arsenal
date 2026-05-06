---
name: team-ralph-loop
description: "Use when executing Hermes Kanban team tasks that reference a local Ralph Loop template, or when a worker/reviewer needs to follow a RALPH.md task loop without Hermes core support."
version: 0.1.0
author: Hermes Atomic Arsenal
license: MIT
metadata:
  hermes:
    tags: [team-mode, kanban, ralph-loop, workflow]
---

# Team Ralph Loop

Use this skill when a Hermes team-mode task references a local `RALPH.md`
template through task text, comments, or metadata such as `loop_ref`.

Ralph Loop is not a Hermes Agent core runtime. Treat it as a local, reviewable
task template that guides one bounded worker iteration.

## Boundaries

- Kanban remains the source of truth for task state, assignment, retry, and
  handoff.
- Profiles provide identity, model, tools, memory, and working directory.
- `RALPH.md` provides task-specific iteration instructions.
- Do not require native Hermes dispatcher support for `loop_ref`.
- Do not install gbrain or self-evolution for this workflow.
- Do not mutate production `hermes-agent` source code automatically.

## Template Locations

Prefer local templates from the installed Hermes home:

```text
$HERMES_HOME/loops/<loop-name>/RALPH.md
```

If the runtime install has not copied loops into `$HERMES_HOME`, use the local
extension repository path:

```text
/home/github/hermes-atomic-arsenal/loops/<loop-name>/RALPH.md
```

Only use templates from trusted local paths supplied by the task, profile, or
deployment docs.

## Worker Procedure

1. Read the Kanban task body, comments, parent summaries, and prior run summary.
2. Resolve `loop_ref` when present. Examples:
   - `loops/bug-hunter`
   - `bug-hunter`
   - `/home/hermes_data/loops/bug-hunter/RALPH.md`
3. Read the referenced `RALPH.md`.
4. Run the template's required preflight checks.
5. Make one bounded change or investigation step.
6. Run the template's required verification checks.
7. Write a compact handoff back to Kanban or the final response.

## Handoff Format

Use this shape in task comments, run summaries, or final handoffs:

```yaml
summary: <one or two sentences>
loop_ref: <template path or name>
loop_iteration: <integer if known>
loop_status: continue | needs_review | blocked | complete
artifacts:
  - <path, diff, command, log, or report>
blocked_reason: <only when blocked>
next_step: <only when continue or needs_review>
```

Do not include hidden chain-of-thought or full scratchpads. Keep only durable
facts another profile needs.

## Review Procedure

When reviewing loop-backed work:

1. Read the worker handoff and artifacts.
2. Read the same `RALPH.md` template if the review depends on loop-specific
   completion criteria.
3. Verify the commands or evidence required by the template.
4. Mark the task `complete`, or return `blocked`/`continue` with a concrete
   fix request.

Preserve the same `loop_ref` when asking for another iteration.

## Safety Rules

- Treat third-party templates like community skills: inspect them before use.
- Do not run destructive commands unless the user or task explicitly approved
  the exact operation.
- Do not let templates override deployment facts from
  `/home/github/hermes-agent/docs/deploy/agent-first.md`.
- If a template conflicts with Hermes team-mode docs, follow the local team-mode
  docs and record the conflict in the handoff.
