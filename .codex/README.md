# .codex configuration

This folder contains project-scoped Codex defaults.

- `approval_policy = "on-request"` keeps potentially sensitive actions reviewable.
- `sandbox_mode = "workspace-write"` lets Codex edit the repository but avoids full machine access.
- `web_search = "disabled"` keeps builds deterministic unless a task explicitly requires current external information.
- Network access inside the workspace-write sandbox is disabled by default.

Keep personal choices such as provider, authentication, telemetry, and model preferences in `~/.codex/config.toml`, not in this repository.
