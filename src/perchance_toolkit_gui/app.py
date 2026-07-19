"""PySide6-based GUI application."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from perchance_toolkit_gui.windows.main_window import MainWindow


class PerchanceGUI(QApplication):
    """Desktop application for perchance.org."""

    def __init__(self) -> None:
        super().__init__(sys.argv)
        self.setApplicationName("perchance-toolkit")
        self.setApplicationVersion("0.1.0")
        self._main_window = MainWindow()

    def run(self) -> int:
        self._main_window.show()
        return self.exec()


def main() -> None:
    app = PerchanceGUI()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
