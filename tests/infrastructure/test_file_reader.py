import pytest

from md5_tui.infrastructure.file_reader import FileReader


def test_iter_file_chunks_reads_file_contents(tmp_path) -> None:
    file_path = tmp_path / "fixture.txt"
    file_path.write_bytes(b"abcdefgh")
    reader = FileReader()

    chunks = list(reader.iter_file_chunks(file_path, chunk_size=3))

    assert chunks == [b"abc", b"def", b"gh"]


def test_iter_file_chunks_raises_for_missing_file(tmp_path) -> None:
    reader = FileReader()

    with pytest.raises(FileNotFoundError):
        list(reader.iter_file_chunks(tmp_path / "missing.txt"))


def test_iter_file_chunks_raises_for_directory(tmp_path) -> None:
    reader = FileReader()

    with pytest.raises(IsADirectoryError):
        list(reader.iter_file_chunks(tmp_path))