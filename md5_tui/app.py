from textual.app import App

from md5_tui.domain.history_service import HistoryService
from md5_tui.domain.md5_service import Md5Service
from md5_tui.infrastructure.clock import SystemClock
from md5_tui.infrastructure.file_reader import FileReader
from md5_tui.ui.controllers import AppState, Md5Controller
from md5_tui.ui.screens import MainScreen


class Md5App(App[None]):
    """Terminal UI for generating MD5 hashes from text and files."""

    TITLE = "MD5 TUI"
    SUB_TITLE = "Text, files, and batch hashing"
    CSS = """
    Screen {
        background: $surface;
    }
    """
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        file_reader = FileReader()
        clock = SystemClock()
        md5_service = Md5Service(file_reader=file_reader, clock=clock)
        history_service = HistoryService()
        state = AppState()
        self.controller = Md5Controller(
            md5_service=md5_service,
            history_service=history_service,
            state=state,
        )

    def on_mount(self) -> None:
        self.push_screen(MainScreen(controller=self.controller))


def run() -> None:
    Md5App().run()