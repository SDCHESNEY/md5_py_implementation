from collections.abc import Iterator
from pathlib import Path


class FileReader:
    def iter_file_chunks(
        self, file_path: Path, chunk_size: int = 65536
    ) -> Iterator[bytes]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if path.is_dir():
            raise IsADirectoryError(str(path))

        with path.open("rb") as handle:
            while True:
                chunk = handle.read(chunk_size)
                if not chunk:
                    break
                yield chunk
