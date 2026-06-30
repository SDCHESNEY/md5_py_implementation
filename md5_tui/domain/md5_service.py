import hashlib
from datetime import datetime
from pathlib import Path
from typing import Iterable, Protocol

from md5_tui.domain.models import HashResult, SourceType


class ChunkReader(Protocol):
    def iter_file_chunks(
        self, file_path: Path, chunk_size: int = 65536
    ) -> Iterable[bytes]: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class Md5Service:
    def __init__(
        self,
        file_reader: ChunkReader,
        clock: Clock,
        chunk_size: int = 65536,
    ) -> None:
        self._file_reader = file_reader
        self._clock = clock
        self._chunk_size = chunk_size

    def hash_text(self, text: str, label: str = "text input") -> HashResult:
        text_bytes = text.encode("utf-8")
        digest = hashlib.md5(text_bytes).hexdigest()
        return HashResult(
            source_type="text",
            label=label,
            md5_hex=digest,
            byte_count=len(text_bytes),
            created_at=self._clock.now(),
        )

    def hash_file(
        self,
        file_path: Path,
        label: str | None = None,
        source_type: SourceType = "file",
    ) -> HashResult:
        digest = hashlib.md5()
        byte_count = 0
        for chunk in self._file_reader.iter_file_chunks(
            file_path, chunk_size=self._chunk_size
        ):
            digest.update(chunk)
            byte_count += len(chunk)

        return HashResult(
            source_type=source_type,
            label=label or file_path.name or str(file_path),
            md5_hex=digest.hexdigest(),
            byte_count=byte_count,
            created_at=self._clock.now(),
        )
