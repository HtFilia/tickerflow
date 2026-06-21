# PLANS.md

Use this file as the execution-plan template for non-trivial Codex tasks.

## Plan template

```markdown
# Plan: <task name>

## Goal
Describe the exact outcome in one or two sentences.

## Non-goals
List tempting work that should not be done in this task.

## Files to inspect first
- `AGENTS.md`
- `README.md`
- `docs/PROJECT_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/QUALITY_AND_VALIDATION.md`

## Proposed changes
1. <small, reviewable change>
2. <small, reviewable change>
3. <small, reviewable change>

## Tests and checks
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy src tests`
- `uv run pytest`

## Recruiter demo requirements
- Update `docs/RECRUITER_DEMO_PLAN.md` when the feature changes the public story.
- Add or refresh screenshots under `docs/assets/screenshots/` when there is UI, Swagger/OpenAPI output, charts, or another visual artifact worth showing.
- Keep demo steps deterministic and based on committed fixtures only.

## Risks
- Numerical approximation risk:
- API compatibility risk:
- Test determinism risk:
- Documentation drift risk:

## Acceptance criteria
- Public APIs are typed and documented.
- Tests cover nominal cases, edge cases, and at least one regression or benchmark invariant.
- All documented checks pass.
- README/docs are updated when behavior changes.
- Recruiter-facing changes include a screenshot plan or demo plan, and actual screenshots when UI or visual output exists.
```

## Planning rules

- Keep plans short enough to review before execution.
- Prefer vertical slices over large rewrites.
- Do not implement optional milestones unless explicitly requested.
- When requirements are ambiguous, make a conservative assumption and record it in the plan.
- When changing numerical code, define the reference value or invariant before writing the implementation.
- For recruiter-facing work, plan the screenshot/demo path before implementation so the repository communicates value quickly to non-specialists.
