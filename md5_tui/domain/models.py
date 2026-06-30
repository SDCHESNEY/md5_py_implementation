from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal


SourceType = Literal["text", "file", "batch-item"]


@dataclass(frozen=True)
class HashRequest:
    source_type: SourceType
    label: str
    text_value: str | None = None
    file_path: Path | None = None


@dataclass(frozen=True)
class HashResult:
    source_type: SourceType
    label: str
    md5_hex: str
    byte_count: int
    created_at: datetime


@dataclass(frozen=True)
class HashFailure:
    label: str
    message: str


@dataclass(frozen=True)
class BatchItemResult:
    label: str
    source_path: str
    md5_hex: str | None
    error_message: str | None

    @property
    def succeeded(self) -> bool:
        return self.error_message is None
