from datetime import datetime, timezone

from md5_tui.domain.history_service import HistoryService
from md5_tui.domain.models import HashResult


def _result(label: str, md5_hex: str) -> HashResult:
    return HashResult(
        source_type="text",
        label=label,
        md5_hex=md5_hex,
        byte_count=1,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_history_service_preserves_order() -> None:
    history = HistoryService()
    first = _result("first", "aaa")
    second = _result("second", "bbb")

    history.add(first)
    history.add(second)

    assert history.list_results() == [first, second]


def test_history_service_clear_removes_results() -> None:
    history = HistoryService()
    history.add(_result("first", "aaa"))

    history.clear()

    assert history.list_results() == []