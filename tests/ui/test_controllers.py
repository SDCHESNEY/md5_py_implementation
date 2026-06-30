from datetime import datetime, timezone

from md5_tui.domain.history_service import HistoryService
from md5_tui.domain.md5_service import Md5Service
from md5_tui.domain.models import HashFailure, HashResult
from md5_tui.infrastructure.file_reader import FileReader
from md5_tui.ui.controllers import AppState, Md5Controller


class FixedClock:
    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time


def _build_controller() -> Md5Controller:
    service = Md5Service(
        file_reader=FileReader(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=timezone.utc)),
    )
    history = HistoryService()
    return Md5Controller(md5_service=service, history_service=history, state=AppState())


def test_hash_current_text_updates_history_and_status() -> None:
    controller = _build_controller()

    outcome = controller.hash_current_text("hello")

    assert isinstance(outcome, HashResult)
    assert outcome.md5_hex == "5d41402abc4b2a76b9719d911017c592"
    assert len(controller.state.history) == 1
    assert "Generated MD5 for text input" in controller.state.status_message


def test_hash_current_file_reports_missing_path() -> None:
    controller = _build_controller()

    outcome = controller.hash_current_file("/tmp/does-not-exist.txt")

    assert isinstance(outcome, HashFailure)
    assert outcome.message == "File not found: /tmp/does-not-exist.txt"
    assert controller.state.history == []


def test_run_batch_continues_after_failure(tmp_path) -> None:
    existing_file = tmp_path / "sample.txt"
    existing_file.write_text("hello", encoding="utf-8")
    missing_file = tmp_path / "missing.txt"
    controller = _build_controller()

    controller.enqueue_file_path(str(existing_file))
    controller.enqueue_file_path(str(missing_file))
    results = controller.run_batch()

    assert len(results) == 2
    assert results[0].succeeded is True
    assert results[1].succeeded is False
    assert results[0].md5_hex == "5d41402abc4b2a76b9719d911017c592"
    assert results[1].error_message == f"File not found: {missing_file}"
    assert len(controller.state.history) == 1