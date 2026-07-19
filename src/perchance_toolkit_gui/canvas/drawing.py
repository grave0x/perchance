"""Canvas drawing widget for generator diagrams."""

from __future__ import annotations

from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene


class DrawingCanvas(QGraphicsView):
    """Interactive canvas for creating and editing generator diagrams."""

    def __init__(self, parent=None) -> None:
        self._scene = QGraphicsScene(self)
        super().__init__(self._scene, parent)
        self.setRenderHints(
            self.renderHints() | QPainter.RenderHint.Antialiasing
        )
