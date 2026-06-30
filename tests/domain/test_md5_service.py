import hashlib
from datetime import datetime, timezone

from md5_tui.domain.md5_service import Md5Service
from md5_tui.infrastructure.file_reader import FileReader


class FixedClock:
    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time


def test_hash_text_returns_known_md5() -> None:
    service = Md5Service(
        file_reader=FileReader(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=timezone.utc)),
    )

    result = service.hash_text("hello")

    assert result.md5_hex == "5d41402abc4b2a76b9719d911017c592"
    assert result.byte_count == 5
    assert result.source_type == "text"


def test_hash_text_supports_empty_string() -> None:
    service = Md5Service(
        file_reader=FileReader(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=timezone.utc)),
    )

    result = service.hash_text("")

    assert result.md5_hex == "d41d8cd98f00b204e9800998ecf8427e"
    assert result.byte_count == 0


def test_hash_file_returns_known_md5(tmp_path) -> None:
    file_path = tmp_path / "hello.txt"
    file_path.write_text("hello", encoding="utf-8")
    service = Md5Service(
        file_reader=FileReader(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=timezone.utc)),
    )

    result = service.hash_file(file_path)

    assert result.md5_hex == "5d41402abc4b2a76b9719d911017c592"
    assert result.byte_count == 5
    assert result.label == "hello.txt"


def test_hash_binary_file_returns_expected_md5(tmp_path) -> None:
    file_path = tmp_path / "sample.bin"
    payload = b"\x00\xffabc\x10"
    file_path.write_bytes(payload)
    service = Md5Service(
        file_reader=FileReader(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=timezone.utc)),
    )

    result = service.hash_file(file_path)

    assert result.md5_hex == hashlib.md5(payload).hexdigest()
    assert result.byte_count == 6