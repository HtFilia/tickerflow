# Codex workflow

This repository is designed to be built incrementally with Codex CLI, Codex App, or the Codex IDE extension.

## Recommended workflow

1. Start a fresh Codex session from the repository root.
2. Ask Codex to read `AGENTS.md`, `README.md`, `PLANS.md`, and the files in `docs/` before changing code.
3. Use plan mode for any non-trivial implementation step.
4. Ask Codex to implement only one milestone or vertical slice at a time.
5. Require tests, linting, formatting, and documentation updates before accepting a diff.
6. Use `/review` after each meaningful change to ask a separate review pass to look for regressions, numerical issues, missing tests, and weak API design.

## Useful Codex CLI commands

```bash
codex
```

Inside the Codex TUI:

```text
/init      # only if AGENTS.md does not exist yet; afterwards keep this curated file
/plan      # ask Codex to propose an execution plan before coding
/review    # review the working tree after implementation
/status    # verify model, approval policy, sandbox, writable roots, context usage
/new       # start a fresh thread in the same repo
```

## Prompting pattern

Use this pattern for implementation requests:

```text
Read AGENTS.md, PLANS.md, README.md, and the relevant docs in docs/.
Work only on the milestone named <milestone>.
Before coding, produce a short execution plan with files to create or modify.
Implement the smallest useful vertical slice.
Add or update tests.
Run the documented checks.
Update docs if behavior or public APIs changed.
Finish with a concise summary of changed files, checks run, and remaining risks.
```

## Review pattern

After Codex implements a change, ask:

```text
Run /review against the current working tree. Focus on numerical correctness, deterministic tests, API consistency, documentation drift, and whether the implementation violates AGENTS.md.
```

## Subagent pattern for larger tasks

For large changes, explicitly request parallel investigation but merge carefully:

```text
Spawn subagents only for read-only exploration. Use one subagent to inspect numerical-method requirements, one to inspect API/test design, and one to inspect docs. Consolidate findings into a single implementation plan before changing files.
```
