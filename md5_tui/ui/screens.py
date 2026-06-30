from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, TabbedContent, TabPane, TextArea

from md5_tui.domain.models import HashFailure, HashResult
from md5_tui.ui.controllers import Md5Controller
from md5_tui.ui.widgets import (
    HistoryTable,
    ResultPanel,
    StatusMessage,
    format_batch_queue,
    format_batch_results,
)


class MainScreen(Screen[None]):
    CSS = """
    #body {
        padding: 1 2;
    }
    #status-message {
        height: 1;
        dock: bottom;
        background: $boost;
        color: $text;
        padding: 0 1;
    }
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        padding: 1;
    }
    TextArea {
        height: 12;
    }
    Input {
        width: 1fr;
    }
    .actions {
        height: auto;
        padding: 1 0;
    }
    ResultPanel, #batch-queue, #batch-results {
        border: round $accent;
        padding: 1;
        min-height: 5;
    }
    HistoryTable {
        height: 1fr;
    }
    """

    def __init__(self, controller: Md5Controller) -> None:
        super().__init__()
        self.controller = controller

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"):
            with TabbedContent(initial="text"):
                with TabPane("Text", id="text"):
                    yield TextArea(self.controller.state.current_text, id="text-input")
                    with Horizontal(classes="actions"):
                        yield Button("Generate MD5", id="hash-text", variant="primary")
                    yield ResultPanel("No result yet.", id="text-result")

                with TabPane("File", id="file"):
                    yield Input(
                        value=self.controller.state.current_file_path,
                        placeholder="Path to file",
                        id="file-input",
                    )
                    with Horizontal(classes="actions"):
                        yield Button("Generate MD5", id="hash-file", variant="primary")
                        yield Button("Add To Batch", id="enqueue-file")
                        yield Button("Run Batch", id="run-batch")
                    yield ResultPanel("No result yet.", id="file-result")
                    yield ResultPanel(format_batch_queue([]), id="batch-queue")
                    yield ResultPanel(format_batch_results([]), id="batch-results")

                with TabPane("History", id="history"):
                    yield HistoryTable(id="history-table")
                    with Horizontal(classes="actions"):
                        yield Button("Clear History", id="clear-history")

        yield StatusMessage(self.controller.state.status_message, id="status-message")
        yield Footer()

    def on_mount(self) -> None:
        history_table = self.query_one("#history-table", HistoryTable)
        history_table.add_columns("Timestamp", "Source", "Label", "MD5", "Bytes")
        history_table.sync_results(self.controller.state.history)
        self._refresh_batch_views()
        self.query_one("#status-message", StatusMessage).show_message(
            self.controller.state.status_message
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "hash-text":
            text_value = self.query_one("#text-input", TextArea).text
            outcome = self.controller.hash_current_text(text_value)
            self._render_outcome(outcome, panel_id="#text-result")
            self._refresh_history_table()
        elif button_id == "hash-file":
            file_path = self.query_one("#file-input", Input).value
            outcome = self.controller.hash_current_file(file_path)
            self._render_outcome(outcome, panel_id="#file-result")
            self._refresh_history_table()
        elif button_id == "enqueue-file":
            file_path = self.query_one("#file-input", Input).value
            outcome = self.controller.enqueue_file_path(file_path)
            self._refresh_batch_views()
            self._render_outcome(outcome, panel_id="#file-result", allow_placeholder=True)
        elif button_id == "run-batch":
            self.controller.run_batch()
            self._refresh_batch_views()
            self._refresh_history_table()
        elif button_id == "clear-history":
            self.controller.clear_history()
            self._refresh_history_table()

        self.query_one("#status-message", StatusMessage).show_message(
            self.controller.state.status_message
        )

    def _refresh_history_table(self) -> None:
        history_table = self.query_one("#history-table", HistoryTable)
        history_table.sync_results(self.controller.state.history)

    def _refresh_batch_views(self) -> None:
        self.query_one("#batch-queue", ResultPanel).update(
            format_batch_queue(self.controller.state.batch_queue)
        )
        self.query_one("#batch-results", ResultPanel).update(
            format_batch_results(self.controller.state.batch_results)
        )

    def _render_outcome(
        self,
        outcome: HashResult | HashFailure,
        panel_id: str,
        allow_placeholder: bool = False,
    ) -> None:
        panel = self.query_one(panel_id, ResultPanel)
        if isinstance(outcome, HashResult):
            if outcome.md5_hex:
                panel.show_result(outcome)
            elif allow_placeholder:
                panel.clear_panel("Queued for batch hashing.")
            else:
                panel.clear_panel()
            return
        panel.show_failure(outcome)
