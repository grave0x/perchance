"""Main application window."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QListWidget,
    QMainWindow,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Primary window with sidebar, editor, and output panes."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("perchance-toolkit")
        self.resize(1200, 800)

        self._build_ui()

    def _build_ui(self) -> None:
        # Sidebar navigation
        self._sidebar = QListWidget()
        self._sidebar.addItems(["Run", "Search", "History", "Favorites", "Settings"])
        self._sidebar.setMaximumWidth(200)

        # Central area: prompt editor + output
        self._prompt_editor = QTextEdit()
        self._prompt_editor.setPlaceholderText("Enter your prompt...")

        self._output_view = QTextEdit()
        self._output_view.setReadOnly(True)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._prompt_editor)
        splitter.addWidget(self._output_view)

        # Layout
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)

        self.setCentralWidget(central)

        dock = QDockWidget("Navigation", self)
        dock.setWidget(self._sidebar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
