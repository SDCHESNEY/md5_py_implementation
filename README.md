# MD5 TUI

MD5 TUI is a Python terminal application for generating MD5 hashes from typed text and files. The project is managed with `uv`, uses `textual` for the user interface, and keeps hashing logic separate from TUI concerns so the core behavior stays easy to test.

## Current Status

The scaffold currently includes:

- text hashing from the TUI
- single-file hashing from the TUI
- batch queue and sequential batch processing
- in-memory session history
- focused automated tests for domain, infrastructure, and controller behavior

The implementation plan and acceptance criteria live in [docs/tech_spec.md](docs/tech_spec.md).

## Requirements

- Python 3.12 or newer
- `uv` installed locally

## Setup

Install dependencies and create the local virtual environment:

```bash
uv sync
```

## Run The Application

Start the TUI with either of the verified entrypoints:

```bash
uv run python -m md5_tui
```

or:

```bash
uv run md5-tui
```

## Test The Project

Run the automated test suite with:

```bash
uv run pytest
```

## TUI Workflow

The current TUI is organized into three tabs:

1. `Text`: paste or type text, then generate its MD5 hash.
2. `File`: hash a single file path, add files to the batch queue, or run batch hashing.
3. `History`: review successful results captured during the current session and clear them.

Press `q` to quit the application.

## Project Layout

```text
md5_tui/
  app.py                 Application entrypoint and dependency wiring
  domain/                Hashing and history logic
  infrastructure/        File and clock adapters
  ui/                    Textual screens, widgets, and controllers
tests/
  domain/
  infrastructure/
  ui/
docs/
  tech_spec.md           Detailed implementation plan
  operations.md          Runbook and operational notes
```

## Operational Notes

Day-to-day commands, validation steps, and troubleshooting notes are documented in [docs/operations.md](docs/operations.md).
