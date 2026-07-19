"""Export generation results to various formats."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from perchance_toolkit.models.generation import ExportFormat, Generation


class ExportService:
    """Handles exporting generations to files."""

    EXPORT_EXTENSIONS = {
        ExportFormat.text: ".txt",
        ExportFormat.markdown: ".md",
        ExportFormat.html: ".html",
        ExportFormat.json: ".json",
    }

    def export(
        self,
        generation: Generation,
        path: Optional[Path] = None,
        fmt: ExportFormat = ExportFormat.markdown,
    ) -> Path:
        """Write generation to a file in the requested format."""
        if path is None:
            ext = self.EXPORT_EXTENSIONS[fmt]
            path = Path.cwd() / f"{generation.generator_id}_{generation.id[:8]}{ext}"
        content = generation.to_export(fmt)
        path.write_text(content)
        return path

    def export_batch(
        self,
        generations: list[Generation],
        output_dir: Path,
        fmt: ExportFormat = ExportFormat.markdown,
    ) -> list[Path]:
        """Export multiple generations to a directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for gen in generations:
            path = self.export(gen, output_dir / self._filename(gen, fmt), fmt)
            paths.append(path)
        return paths

    @staticmethod
    def _filename(gen: Generation, fmt: ExportFormat) -> str:
        ext = ExportService.EXPORT_EXTENSIONS[fmt]
        return f"{gen.generator_id}_{gen.id[:8]}{ext}"
