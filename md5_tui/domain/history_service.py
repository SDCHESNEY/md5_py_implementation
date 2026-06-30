from md5_tui.domain.models import HashResult


class HistoryService:
    def __init__(self) -> None:
        self._results: list[HashResult] = []

    def add(self, result: HashResult) -> None:
        self._results.append(result)

    def list_results(self) -> list[HashResult]:
        return list(self._results)

    def clear(self) -> None:
        self._results.clear()
