"""Settings dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox


class SettingsDialog(QDialog):
    """Application preferences dialog."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")

        layout = QFormLayout(self)
        layout.addRow("Theme", QLineEdit("dark"))
        self._max_history = QSpinBox()
        self._max_history.setValue(200)
        layout.addRow("Max History", self._max_history)
