# SPDX-License-Identifier: GPL-3.0-or-later
"""Tabla de récords por modo (10 mejores)."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from .paths import data_dir

MAX_ENTRIES = 10


def _sort_key(mode: str):
    if mode == "sprint":
        return lambda e: (e["frames"], -e["score"])
    return lambda e: (-e["score"], -e["lines"])


class HighScores:
    def __init__(self, path: Path | None = None):
        self.path = path or data_dir() / "scores.json"
        self.tables: dict[str, list[dict]] = {}

    def load(self) -> HighScores:
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.tables = {k: v for k, v in data.items() if isinstance(v, list)}
        except (OSError, ValueError):
            self.tables = {}
        return self

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.tables, fh, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except OSError:
            pass

    def table(self, mode: str) -> list[dict]:
        return self.tables.get(mode, [])

    def best(self, mode: str) -> dict | None:
        table = self.table(mode)
        return table[0] if table else None

    @staticmethod
    def make_entry(game, name: str = "") -> dict:
        return {
            "name": name,
            "score": game.score,
            "lines": game.lines,
            "level": game.level,
            "frames": game.frames,
            "start_level": game.rules.start_level,
            "date": date.today().isoformat(),
        }

    def qualifies(self, mode: str, entry: dict, completed: bool) -> bool:
        # Los modos con objetivo solo cuentan si se ha completado el objetivo.
        if mode in ("btype", "sprint") and not completed:
            return False
        if mode == "marathon" and entry["score"] <= 0:
            return False
        table = self.table(mode)
        if len(table) < MAX_ENTRIES:
            return True
        key = _sort_key(mode)
        return key(entry) < key(table[-1])

    def add(self, mode: str, entry: dict) -> int:
        """Añade la entrada y devuelve su posición (0 = primera)."""
        table = list(self.table(mode))
        table.append(entry)
        table.sort(key=_sort_key(mode))
        self.tables[mode] = table[:MAX_ENTRIES]
        self.save()
        return self.tables[mode].index(entry) if entry in self.tables[mode] else -1
