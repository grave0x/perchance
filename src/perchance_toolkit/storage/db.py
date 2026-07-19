"""SQLite-backed persistence for history, favorites, and cache."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Boolean,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


class GenerationRow(Base):
    __tablename__ = "generations"

    id = Column(String, primary_key=True)
    generator_id = Column(String, nullable=False, index=True)
    generator_title = Column(String, default="")
    prompt = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now())
    favorite = Column(Boolean, default=False)
    tags = Column(String, default="")
    duration_ms = Column(Integer, nullable=True)


class Database:
    """Local SQLite store for generation history and metadata."""

    def __init__(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = Path.home() / ".local" / "share" / "perchance-toolkit" / "history.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(self._engine)

    @property
    def session(self) -> Session:
        return self._session_factory()

    def save_generation(self, generation: GenerationRow) -> None:
        with self.session as s:
            s.merge(generation)
            s.commit()

    def get_history(
        self, limit: int = 50, offset: int = 0
    ) -> list[GenerationRow]:
        with self.session as s:
            return (
                s.query(GenerationRow)
                .order_by(GenerationRow.created.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

    def get_favorites(self) -> list[GenerationRow]:
        with self.session as s:
            return (
                s.query(GenerationRow)
                .filter(GenerationRow.favorite.is_(True))
                .order_by(GenerationRow.created.desc())
                .all()
            )

    def toggle_favorite(self, generation_id: str) -> bool:
        """Toggle favorite status, returns new state."""
        with self.session as s:
            row = s.query(GenerationRow).filter_by(id=generation_id).first()
            if row is None:
                return False
            row.favorite = not row.favorite  # type: ignore[assignment]
            s.commit()
            return row.favorite  # type: ignore[return-value]

    def delete_generation(self, generation_id: str) -> bool:
        with self.session as s:
            row = s.query(GenerationRow).filter_by(id=generation_id).first()
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True
