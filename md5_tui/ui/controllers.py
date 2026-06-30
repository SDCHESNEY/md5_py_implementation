from dataclasses import dataclass, field
from pathlib import Path

from md5_tui.domain.history_service import HistoryService
from md5_tui.domain.md5_service import Md5Service
from md5_tui.domain.models import BatchItemResult, HashFailure, HashResult


HashOutcome = HashResult | HashFailure


@dataclass
class AppState:
    active_tab: str = "text"
    current_text: str = ""
    current_file_path: str = ""
    batch_queue: list[str] = field(default_factory=list)
    batch_results: list[BatchItemResult] = field(default_factory=list)
    history: list[HashResult] = field(default_factory=list)
    status_message: str = "Ready."
    text_outcome: HashOutcome | None = None
    file_outcome: HashOutcome | None = None


class Md5Controller:
    def __init__(
        self,
        md5_service: Md5Service,
        history_service: HistoryService,
        state: AppState,
    ) -> None:
        self._md5_service = md5_service
        self._history_service = history_service
        self.state = state

    def hash_current_text(self, text: str) -> HashOutcome:
        self.state.current_text = text
        result = self._md5_service.hash_text(text)
        self._history_service.add(result)
        self.state.history = self._history_service.list_results()
        self.state.text_outcome = result
        self.state.status_message = (
            f"Generated MD5 for text input ({result.byte_count} bytes)."
        )
        return result

    def hash_current_file(self, file_path: str) -> HashOutcome:
        normalized_path = file_path.strip()
        self.state.current_file_path = normalized_path
        if not normalized_path:
            failure = HashFailure(label="file", message="File path is required.")
            self.state.file_outcome = failure
            self.state.status_message = failure.message
            return failure

        try:
            path = Path(normalized_path)
            result = self._md5_service.hash_file(path, label=path.name or str(path))
        except OSError as exc:
            failure = HashFailure(
                label=normalized_path,
                message=self._format_file_error(normalized_path, exc),
            )
            self.state.file_outcome = failure
            self.state.status_message = failure.message
            return failure

        self._history_service.add(result)
        self.state.history = self._history_service.list_results()
        self.state.file_outcome = result
        self.state.status_message = (
            f"Generated MD5 for file '{result.label}' ({result.byte_count} bytes)."
        )
        return result

    def enqueue_file_path(self, file_path: str) -> HashOutcome:
        normalized_path = file_path.strip()
        self.state.current_file_path = normalized_path
        if not normalized_path:
            failure = HashFailure(label="file", message="File path is required.")
            self.state.file_outcome = failure
            self.state.status_message = failure.message
            return failure
        if normalized_path not in self.state.batch_queue:
            self.state.batch_queue.append(normalized_path)
        self.state.status_message = (
            f"Queued {len(self.state.batch_queue)} file(s) for batch hashing."
        )
        return HashResult(
            source_type="file",
            label=normalized_path,
            md5_hex="",
            byte_count=0,
            created_at=self.state.history[-1].created_at if self.state.history else self._md5_service.hash_text("").created_at,
        )

    def run_batch(self) -> list[BatchItemResult]:
        if not self.state.batch_queue:
            self.state.status_message = "Batch queue is empty."
            self.state.batch_results = []
            return []

        results: list[BatchItemResult] = []
        for raw_path in self.state.batch_queue:
            path = Path(raw_path)
            try:
                hash_result = self._md5_service.hash_file(
                    path,
                    label=path.name or str(path),
                    source_type="batch-item",
                )
            except OSError as exc:
                results.append(
                    BatchItemResult(
                        label=path.name or str(path),
                        source_path=str(path),
                        md5_hex=None,
                        error_message=self._format_file_error(str(path), exc),
                    )
                )
                continue

            self._history_service.add(hash_result)
            results.append(
                BatchItemResult(
                    label=hash_result.label,
                    source_path=str(path),
                    md5_hex=hash_result.md5_hex,
                    error_message=None,
                )
            )

        self.state.history = self._history_service.list_results()
        self.state.batch_results = results
        success_count = sum(1 for item in results if item.succeeded)
        failure_count = len(results) - success_count
        self.state.status_message = (
            f"Batch complete: {success_count} succeeded, {failure_count} failed."
        )
        return results

    def clear_history(self) -> None:
        self._history_service.clear()
        self.state.history = []
        self.state.status_message = "History cleared."

    @staticmethod
    def _format_file_error(file_path: str, exc: OSError) -> str:
        if isinstance(exc, FileNotFoundError):
            return f"File not found: {file_path}"
        if isinstance(exc, IsADirectoryError):
            return f"Expected a file but received a directory: {file_path}"
        if isinstance(exc, PermissionError):
            return f"Permission denied while reading: {file_path}"
        return f"Unable to hash file '{file_path}': {exc}"
