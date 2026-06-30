# Operations Guide

## Purpose

This document covers the daily development and local operation workflow for the MD5 TUI scaffold.

## Environment Setup

Create or update the project environment:

```bash
uv sync
```

This command creates `.venv/` if needed and installs both runtime and development dependencies from the current project configuration.

## Run Commands

Launch the application:

```bash
uv run python -m md5_tui
```

Alternative script entrypoint:

```bash
uv run md5-tui
```

Run tests:

```bash
uv run pytest
```

## Development Workflow

Recommended local workflow:

1. Run `uv sync` after dependency or metadata changes.
2. Make focused code changes in one layer at a time.
3. Run `uv run pytest` before concluding a change.
4. Update [docs/tech_spec.md](docs/tech_spec.md) or [README.md](../README.md) when behavior or commands change.

## Current Application Behavior

The current scaffold supports:

- hashing UTF-8 text input
- hashing files using chunked binary reads
- queuing multiple files for sequential batch hashing
- tracking successful results in session-only history
- reporting common file errors in the TUI status area

## Key Paths

- Application entrypoint: [md5_tui/app.py](../md5_tui/app.py)
- Hashing service: [md5_tui/domain/md5_service.py](../md5_tui/domain/md5_service.py)
- File reader: [md5_tui/infrastructure/file_reader.py](../md5_tui/infrastructure/file_reader.py)
- TUI screen layout: [md5_tui/ui/screens.py](../md5_tui/ui/screens.py)
- Controller state transitions: [md5_tui/ui/controllers.py](../md5_tui/ui/controllers.py)

## Troubleshooting

### `uv sync` fails

Check that:

- `uv` is installed and available on `PATH`
- `pyproject.toml` is valid
- the `md5_tui/` package directory still exists and matches the configured package name

### `uv run pytest` fails

Check that:

- dependencies are installed with `uv sync`
- recent code changes did not break the domain or controller interfaces
- file-path related tests are not relying on machine-specific paths

### The TUI starts but hashing fails for a file

Check that:

- the file path exists
- the path points to a file rather than a directory
- the current user has permission to read the file

## Validation Baseline

The scaffold has been validated with:

```bash
uv sync
uv run pytest
```

At the time of writing, the automated suite passes against the scaffolded project structure.