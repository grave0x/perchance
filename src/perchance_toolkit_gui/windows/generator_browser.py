"""Generator search and browse window."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QVBoxLayout


class GeneratorBrowser(QDialog):
    """Dialog for searching and browsing generators."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Browse Generators")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search generators...")
        self._results_list = QListWidget()
        layout.addWidget(self._search_input)
        layout.addWidget(self._results_list)
