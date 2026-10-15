# SPDX-License-Identifier: GPL-3.0-or-later
"""Tablero de juego: una cuadrícula con filas ocultas por encima de las visibles."""

from __future__ import annotations

import random
from collections.abc import Iterable

from .pieces import PIECES


class Board:
    def __init__(self, width: int = 10, visible_height: int = 20, hidden: int = 2):
        self.width = width
        self.visible_height = visible_height
        self.hidden = hidden
        self.height = visible_height + hidden
        # Cada celda es None (vacía) o la letra de la pieza que la ocupa.
        self.cells: list[list[str | None]] = [[None] * width for _ in range(self.height)]

    def is_free(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and self.cells[y][x] is None

    def fits(self, cells: Iterable[tuple[int, int]]) -> bool:
        return all(self.is_free(x, y) for x, y in cells)

    def place(self, cells: Iterable[tuple[int, int]], kind: str) -> None:
        for x, y in cells:
            self.cells[y][x] = kind

    def full_rows(self) -> list[int]:
        return [y for y, row in enumerate(self.cells) if all(c is not None for c in row)]

    def clear_rows(self, rows: Iterable[int]) -> None:
        doomed = set(rows)
        kept = [row for y, row in enumerate(self.cells) if y not in doomed]
        self.cells = [[None] * self.width for _ in doomed] + kept

    def add_garbage(self, rows: int, filled: int, rng: random.Random) -> None:
        """Rellena las `rows` filas inferiores con `filled` bloques cada una
        (como las "filas prellenadas" de Quadrapassel o el tipo B del NES).
        Siempre deja al menos un hueco por fila."""
        filled = max(1, min(self.width - 1, filled))
        rows = max(0, min(self.visible_height - 4, rows))
        for y in range(self.height - rows, self.height):
            columns = rng.sample(range(self.width), filled)
            self.cells[y] = [None] * self.width
            for x in columns:
                self.cells[y][x] = rng.choice(PIECES)

    def stack_height(self) -> int:
        """Altura de la pila (filas ocupadas contando desde abajo)."""
        for y, row in enumerate(self.cells):
            if any(c is not None for c in row):
                return self.height - y
        return 0
