import json
import sqlite3
from pathlib import Path
from src.config import settings
from src.domain.schemas import Kit


class SqliteStore:
    def __init__(self, database: str | Path | None = None):
        self.database = str(database or settings.data_dir / "sloth.db")
        self._memory_connection = sqlite3.connect(":memory:") if self.database == ":memory:" else None
        if self.database != ":memory:":
            Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return self._memory_connection or sqlite3.connect(self.database)

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS kits (id TEXT PRIMARY KEY, title TEXT NOT NULL, kit_json TEXT NOT NULL)")

    def save_kit(self, kit: Kit) -> None:
        with self._connect() as connection:
            connection.execute("INSERT OR REPLACE INTO kits VALUES (?, ?, ?)", (kit.id, kit.title, kit.model_dump_json()))

    def get_kit(self, kit_id: str) -> Kit:
        with self._connect() as connection:
            row = connection.execute("SELECT kit_json FROM kits WHERE id = ?", (kit_id,)).fetchone()
        if row is None:
            raise KeyError(f"Kit not found: {kit_id}")
        return Kit.model_validate_json(row[0])

    def list_kits(self) -> list[tuple[str, str]]:
        with self._connect() as connection:
            return connection.execute("SELECT id, title FROM kits ORDER BY rowid DESC").fetchall()
