# MD5 TUI Technical Specification

## 1. Purpose

Build a Python-based terminal user interface application that generates MD5 hashes for:

- user-provided text
- individual files, regardless of whether their contents are text or binary
- multiple files processed in sequence

The application must provide a clear TUI workflow, deterministic hashing behavior, and strong test coverage. Development, dependency management, and execution must use `uv`.

## 2. Goals

- Provide a terminal-first workflow for hashing text and files without requiring GUI tooling.
- Use the Python standard library for the hashing implementation.
- Separate TUI concerns from hashing and file-processing logic.
- Support large files through streamed reads rather than loading entire files into memory.
- Make the core hashing logic independently testable without the TUI runtime.

## 3. Non-Goals

- Cryptographic verification beyond MD5.
- Recursive directory hashing in the initial release.
- Parallel hashing in the initial release.
- Remote file access, cloud storage, or network-based inputs.
- File mutation, checksum writing, or checksum verification against manifest files in the initial release.

## 4. User Stories

1. As a user, I want to paste or type text and immediately see its MD5 hash.
2. As a user, I want to provide a file path and compute the MD5 hash of that file.
3. As a user, I want binary files to hash correctly without special handling.
4. As a user, I want invalid paths and read errors to produce clear terminal feedback.
5. As a user, I want to review recent results during the current session.
6. As a user, I want to copy or export the computed hash from the terminal session.

## 5. Functional Requirements

### 5.1 Input Modes

- Text input mode:
  - accept typed or pasted text
  - allow empty string hashing, which must produce the correct MD5 for empty content
- File input mode:
  - accept a path to an existing file
  - read file contents as bytes
  - support text files, binary files, and large files
- Batch input mode:
  - accept multiple file paths in one session
  - display per-file success or failure

### 5.2 Output

- Display lowercase hexadecimal MD5 output.
- Show the input source type with the result, such as `text`, `file`, or `batch-item`.
- Preserve a session-local results list with timestamp, input label, and hash value.
- Provide a clear success/failure status message after each action.

### 5.3 Error Handling

- Reject non-existent file paths with a readable error.
- Reject directories when a file is expected.
- Surface permission errors and read failures without crashing the TUI.
- Handle invalid user actions in the current screen with inline status feedback.

### 5.4 Performance And Reliability

- Hash file data using chunked reads.
- Avoid blocking the interface for noticeable periods without showing progress or busy status.
- Keep hashing logic deterministic across repeated runs.

## 6. Technical Design

### 6.1 Stack

- Python 3.12+
- `uv` for environment, dependency, and command management
- `textual` for the TUI layer
- `hashlib` from the standard library for MD5 generation
- `pathlib` for path handling
- `pytest` for tests

### 6.2 Proposed Package Layout

```text
md5_tui/
  __init__.py
  __main__.py
  app.py
  domain/
    __init__.py
    models.py
    md5_service.py
    history_service.py
  infrastructure/
    __init__.py
    file_reader.py
    clock.py
  ui/
    __init__.py
    screens.py
    widgets.py
    controllers.py
tests/
  domain/
  infrastructure/
  ui/
```

### 6.3 Architecture Principles

- The domain layer owns hashing rules, result models, and validation outcomes.
- The infrastructure layer owns side effects such as file I/O and timestamps.
- The UI layer owns event handling, layout, focus control, and rendering.
- The TUI should call small controller methods that orchestrate domain services.
- Domain services should not import TUI classes.

### 6.4 Core Domain Model

Suggested models:

- `HashRequest`
  - `source_type: Literal["text", "file"]`
  - `label: str`
  - `text_value: str | None`
  - `file_path: Path | None`
- `HashResult`
  - `source_type: Literal["text", "file"]`
  - `label: str`
  - `md5_hex: str`
  - `byte_count: int`
  - `created_at: datetime`
- `HashFailure`
  - `label: str`
  - `message: str`

### 6.5 Hashing Behavior

#### Text hashing

- Encode text with UTF-8 before hashing.
- Preserve the text exactly as entered, including newlines and trailing spaces.
- Do not normalize line endings automatically.

#### File hashing

- Open files in binary mode.
- Read in fixed-size chunks, such as 64 KB.
- Feed each chunk into `hashlib.md5()` until EOF.
- Return the final lowercase hexadecimal digest.

### 6.6 TUI Screen Design

Recommended initial screens/panels:

1. Main menu / tab selector
   - switch between `Text`, `File`, and `History`
2. Text hash panel
   - multiline text area
   - `Generate MD5` action
   - result display area
3. File hash panel
   - input for file path
   - optional button to add path to batch queue
   - `Generate MD5` action
   - queue/result table
4. History panel
   - session-only list of recent successful hashes
   - action to clear history

### 6.7 State Management

- Maintain a single application state object at the app/controller layer.
- Store:
  - active screen or tab
  - current text input
  - current file path input
  - current batch queue
  - current status message
  - session history
- Keep state transitions explicit through controller methods such as:
  - `hash_current_text()`
  - `hash_current_file()`
  - `enqueue_file_path()`
  - `run_batch()`
  - `clear_history()`

### 6.8 Error Translation Boundary

- Core services may raise precise exceptions such as `FileNotFoundError`, `IsADirectoryError`, or custom validation exceptions.
- UI controllers must translate these into user-readable status messages.
- Stack traces should not be shown in the normal interactive flow.

### 6.9 Session History

- Keep history in memory for the current application session.
- Each item should include:
  - source type
  - label
  - md5 value
  - byte count
  - timestamp
- Persistent storage is optional and should be deferred to a later enhancement.

## 7. External Dependencies

Recommended dependency set:

- Runtime:
  - `textual`
- Development:
  - `pytest`
  - `pytest-asyncio` if required by the chosen TUI test strategy

Recommended setup commands:

```bash
uv init
uv add textual
uv add --dev pytest pytest-asyncio
uv sync
```

## 8. Execution Commands

```bash
uv run python -m md5_tui
uv run pytest
```

## 9. Implementation Phases

### Phase 1: Project Foundation And Core Hashing

#### Scope

- Initialize the Python project for `uv` workflows.
- Create the package structure.
- Implement the core MD5 services for text and file hashing.
- Implement domain models and error handling.
- Add unit tests for the domain and file-reading logic.

#### Deliverables

- `pyproject.toml` configured for the application
- `md5_tui/domain/md5_service.py`
- `md5_tui/infrastructure/file_reader.py`
- initial tests for hashing behavior

#### Acceptance Criteria

1. The application can hash a provided text string using UTF-8 encoding.
2. The application can hash a file by path using chunked binary reads.
3. Empty text input produces the known MD5 value `d41d8cd98f00b204e9800998ecf8427e`.
4. Invalid file paths raise a predictable, test-covered failure.
5. All phase tests pass through `uv run pytest`.

#### Associated Tests

- Unit test: text hashing returns known MD5 for `"hello"`.
- Unit test: text hashing returns the known empty-string MD5.
- Unit test: file hashing matches a known fixture file digest.
- Unit test: binary fixture hashing matches a known digest.
- Unit test: missing file path raises `FileNotFoundError` or mapped domain error.
- Unit test: directory path raises `IsADirectoryError` or mapped domain error.

### Phase 2: Initial TUI Workflow

#### Scope

- Build the main TUI application shell.
- Add separate panels for text and file hashing.
- Display hash results and status messages.
- Connect UI actions to controller methods and domain services.

#### Deliverables

- `md5_tui/app.py`
- `md5_tui/ui/screens.py`
- `md5_tui/ui/controllers.py`
- interactive text and file hashing flow

#### Acceptance Criteria

1. Users can enter text in the TUI and generate an MD5 result without leaving the app.
2. Users can enter a file path in the TUI and generate a file hash.
3. Invalid user inputs produce inline status feedback rather than crashing the app.
4. The UI remains responsive during typical hashing operations.
5. Focus movement and action triggers are keyboard accessible.

#### Associated Tests

- UI test: submitting text input renders the expected MD5 output.
- UI test: submitting a valid file path renders the expected MD5 output.
- UI test: submitting an invalid path renders an error message.
- UI test: switching between text and file workflows preserves local form state as designed.
- Integration test: controller calls domain service and updates view state correctly.

### Phase 3: Batch Processing And Session History

#### Scope

- Support adding multiple file paths to a queue.
- Process queued files sequentially.
- Record successful results in session history.
- Display per-item failures without stopping the full batch.

#### Deliverables

- batch queue state and controls
- history panel or history table
- history service for session storage

#### Acceptance Criteria

1. Users can add multiple file paths before starting batch hashing.
2. Each batch item shows a success result or a readable failure.
3. Successful results appear in session history with timestamps.
4. A failed file does not prevent later batch items from being processed.
5. History can be cleared from the UI.

#### Associated Tests

- Unit test: history service stores and clears items deterministically.
- Integration test: batch processing continues after a single file failure.
- UI test: queue display updates after adding and removing files.
- UI test: history view renders completed results.
- Integration test: timestamps are injected via a controllable clock abstraction.

### Phase 4: Polish, Packaging, And Documentation

#### Scope

- Improve keyboard shortcuts and status messaging.
- Add loading indicators for longer-running file operations.
- Finalize README and operational docs.
- Prepare the app for repeatable local execution.

#### Deliverables

- documented keyboard shortcuts
- user-facing run instructions
- stable packaging and launch entrypoint
- fixture coverage for representative file types

#### Acceptance Criteria

1. Users can discover core actions from visible labels or documented shortcuts.
2. Larger file hashing provides a visible busy state.
3. Local setup, run, and test commands are documented and accurate.
4. The application launches successfully through the documented `uv run` command.
5. Documentation reflects the actual implemented workflows.

#### Associated Tests

- UI test: busy indicator appears during mocked long-running file hashing.
- Smoke test: application module imports and launches without configuration errors.
- Documentation check: listed commands align with the project entrypoint and test commands.

## 10. Test Strategy

### 10.1 Unit Tests

Focus on deterministic, side-effect-light logic:

- text hashing
- file hashing
- validation and error mapping
- history storage behavior

### 10.2 Integration Tests

Focus on component boundaries:

- controller to domain-service integration
- file reader plus hashing service integration
- batch workflow behavior

### 10.3 UI Tests

Use the TUI framework's testing utilities to validate:

- keyboard-driven navigation
- form submission
- status message rendering
- result rendering
- history updates

### 10.4 Test Fixtures

Include fixtures for:

- small plain-text files
- empty files
- small binary files
- filenames with spaces
- unreadable or invalid path scenarios where practical

## 11. Risks And Mitigations

- Risk: TUI framework complexity slows early delivery.
  - Mitigation: keep the first working UI minimal and push advanced polish to later phases.
- Risk: large file operations block the UI event loop.
  - Mitigation: isolate hashing work behind controller actions and add visible busy state before optimization.
- Risk: inconsistent treatment of text input across platforms.
  - Mitigation: document UTF-8 encoding and preserve raw input exactly as entered.
- Risk: binary fixtures are hard to inspect manually.
  - Mitigation: store expected digests in tests and keep fixture files small.

## 12. Definition Of Done

The solution is complete when:

1. The application hashes text and files correctly through the TUI.
2. The architecture keeps hashing logic testable outside the UI runtime.
3. The phased acceptance criteria are satisfied.
4. The documented `uv run` and `uv run pytest` commands work as written.
5. The application provides clear status feedback for both success and failure cases.