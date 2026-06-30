# Project Guidelines

## Python Workflow

- Use Python 3 with explicit type hints for public functions and non-trivial internal helpers.
- Manage dependencies, virtual environments, and lockfiles with `uv`.
- Run project commands through `uv run ...` instead of invoking `python`, `pip`, or tooling directly.
- Add runtime dependencies with `uv add ...` and development dependencies with `uv add --dev ...`.
- Prefer standard-library modules when they keep the implementation clear and small.

## TUI Architecture

- Build the application as a terminal-first TUI, with input handling and screen rendering separated from core business logic.
- Keep state transitions predictable and localized; avoid mixing terminal output code with hashing, parsing, or other domain behavior.
- Design command handlers and view components to be small, testable units.
- Favor user-visible feedback for long-running or invalid operations instead of silent failures.

## Code Style

- Use `pathlib` instead of manual path string manipulation.
- Prefer small functions, descriptive names, and straightforward control flow over clever abstractions.
- Avoid global mutable state unless it is required for a single application-level runtime object.
- Raise precise exceptions in core logic and translate them into clear terminal messages at the UI boundary.

## Build And Test

- Install or update dependencies with `uv sync`.
- Run the application with `uv run python -m <package>` or the configured `uv run` entrypoint.
- Run tests with `uv run pytest`.
- When adding features, include or update focused tests for the affected logic where practical.

## Conventions

- Keep side effects at the edges of the application.
- Prefer deterministic functions for hashing and transformation logic so they can be tested without the TUI runtime.
- Document non-obvious terminal behavior, keyboard shortcuts, and startup commands in project docs as the app grows.