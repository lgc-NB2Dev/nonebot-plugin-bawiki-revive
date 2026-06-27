# AGENTS.md

First: This project expects the working root to be github repo `lgc-NB2Dev/workspace` because some recommended workspace-level files is not stored in this plugin project. If you are not working from that root, stop and notify the user.

## Commands

NOTE: The following command are expected to be run under the plugin repo root rather than the workspace root.

```bash
uv run pytest
```

## Structure

To be added

## Rules

- Keep test coverage as high as possible to avoid dead code. Code included in the current runtime's coverage scope should be covered unless it is version-specific, dependency-gated, or an intentional error path that is impractical to trigger safely.
- Async HTTP clients such as `httpx.AsyncClient` subclasses should be used with `async with` or otherwise explicitly closed; do not create a client and immediately call request methods on it without a close boundary.

## Gotchas

Currently empty
