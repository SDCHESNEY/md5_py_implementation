from collections.abc import Sequence

from textual.widgets import DataTable, Static

from md5_tui.domain.models import BatchItemResult, HashFailure, HashResult


class StatusMessage(Static):
    def show_message(self, message: str) -> None:
        self.update(message or "Ready.")


class ResultPanel(Static):
    def clear_panel(self, placeholder: str = "No result yet.") -> None:
        self.update(placeholder)

    def show_result(self, result: HashResult) -> None:
        self.update(
            "\n".join(
                [
                    f"Source: {result.source_type}",
                    f"Label: {result.label}",
                    f"Bytes: {result.byte_count}",
                    f"MD5: {result.md5_hex}",
                ]
            )
        )

    def show_failure(self, failure: HashFailure) -> None:
        self.update(f"Error: {failure.message}")


class HistoryTable(DataTable):
    def sync_results(self, results: Sequence[HashResult]) -> None:
        self.clear(columns=False)
        for result in results:
            self.add_row(
                result.created_at.isoformat(),
                result.source_type,
                result.label,
                result.md5_hex,
                str(result.byte_count),
            )


def format_batch_results(results: Sequence[BatchItemResult]) -> str:
    if not results:
        return "No batch results yet."

    lines: list[str] = []
    for item in results:
        if item.succeeded:
            lines.append(f"OK   {item.label}: {item.md5_hex}")
        else:
            lines.append(f"FAIL {item.label}: {item.error_message}")
    return "\n".join(lines)


def format_batch_queue(batch_queue: Sequence[str]) -> str:
    if not batch_queue:
        return "No files queued."
    return "\n".join(f"- {path}" for path in batch_queue)
