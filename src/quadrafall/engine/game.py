# SPDX-License-Identifier: GPL-3.0-or-later
"""Reglas del juego. Todo avanza por fotogramas a 60 por segundo, como en el NES,
de modo que velocidades, DAS y retardos se expresan en fotogramas."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, fields

from .board import Board
from .pieces import PIECES, ROTATION_SYSTEMS
from .randomizer import RANDOMIZERS

FPS = 60
QUEUE_SIZE = 6


class Action:
    LEFT = "left"
    RIGHT = "right"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    HOLD = "hold"
    PAUSE = "pause"
    ALL = (LEFT, RIGHT, SOFT_DROP, HARD_DROP, ROTATE_CW, ROTATE_CCW, HOLD, PAUSE)


# Puntos del NES por 1, 2, 3 y 4 líneas, multiplicados por (nivel + 1).
LINE_SCORES = (0, 40, 100, 300, 1200)
# Fotogramas que tarda la pieza en bajar una fila en los niveles 0-9 del NES.
_NES_GRAVITY = (48, 43, 38, 33, 28, 23, 18, 13, 8, 6)

MODES = ("marathon", "btype", "sprint")
MODE_GOALS = {"marathon": None, "btype": 25, "sprint": 40}


def gravity_frames(level: int) -> int:
    if level < 10:
        return _NES_GRAVITY[level]
    if level < 13:
        return 5
    if level < 16:
        return 4
    if level < 19:
        return 3
    if level < 29:
        return 2
    return 1


def level_for_lines(start_level: int, lines: int) -> int:
    """Progresión de nivel del NES: la primera subida depende del nivel inicial,
    después se sube cada 10 líneas."""
    first = min(start_level * 10 + 10, max(100, start_level * 10 - 50))
    if lines < first:
        return start_level
    return start_level + 1 + (lines - first) // 10


def nes_entry_delay(rows_from_bottom: int) -> int:
    """ARE del NES: 10 fotogramas abajo del todo, hasta 18 cuanto más alto se fija."""
    if rows_from_bottom <= 2:
        return 10
    return min(18, 10 + 2 * ((rows_from_bottom - 3) // 4 + 1))


@dataclass
class GameRules:
    mode: str = "marathon"
    start_level: int = 0
    rotation: str = "nes_plus"      # "nes", "nes_plus", "srs"
    randomizer: str = "nes"         # "nes", "bag", "random"
    hold: bool = True
    next_count: int = 3             # 0-5 piezas visibles
    hard_drop: bool = True
    lock_delay: int = 20            # margen mínimo apoyada (fotogramas); 0 = como el NES
    lock_resets: int = 6            # movimientos apoyada que reinician ese margen
    das: int = 12                   # fotogramas antes de autorrepetir
    arr: int = 4                    # fotogramas entre repeticiones (0 = instantáneo)
    soft_drop_frames: int = 2       # fotogramas por fila con bajada suave
    entry_delay: int = -1           # -1 = como el NES (10-18 según altura)
    line_clear_frames: int = 20
    garbage_rows: int = 0
    garbage_density: int = 7        # bloques por fila prellenada (1-9)

    @classmethod
    def from_dict(cls, data: dict) -> GameRules:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ActivePiece:
    kind: str
    rotation: int
    x: int
    y: int


class Game:
    def __init__(self, rules: GameRules, seed: int | None = None):
        self.rules = rules
        self.rng = random.Random(seed)
        self.system = ROTATION_SYSTEMS[rules.rotation]
        self.randomizer = RANDOMIZERS[rules.randomizer](self.rng)
        self.board = Board()
        if rules.garbage_rows:
            self.board.add_garbage(rules.garbage_rows, rules.garbage_density, self.rng)
        self.queue = [self.randomizer.next() for _ in range(QUEUE_SIZE)]
        self.goal = MODE_GOALS.get(rules.mode)

        self.piece: ActivePiece | None = None
        self.held: str | None = None
        self.hold_used = False
        self.score = 0
        self.lines = 0
        self.level = rules.start_level
        self.stats = {kind: 0 for kind in PIECES}
        self.tetris_lines = 0
        self.frames = 0
        self.state = "falling"          # "falling", "are", "clearing", "over", "won"
        self.timer = 0
        self.clearing_rows: list[int] = []
        self.events: list[str] = []     # sonidos/efectos producidos en el último fotograma

        self._das_dir = 0
        self._das_counter = 0
        self._last_dir = 0
        self._gravity_counter = 0
        self._lock_timer = 0
        self._lock_resets_used = 0
        self._lowest_y = 0
        self._lock_row = 0

        self._spawn()

    # --- consultas -------------------------------------------------------------

    @property
    def finished(self) -> bool:
        return self.state in ("over", "won")

    @property
    def preview(self) -> list[str]:
        return self.queue[: self.rules.next_count]

    @property
    def clear_progress(self) -> float:
        if self.state != "clearing" or self.rules.line_clear_frames <= 0:
            return 0.0
        return 1.0 - self.timer / self.rules.line_clear_frames

    @property
    def tetris_rate(self) -> float:
        return self.tetris_lines / self.lines if self.lines else 0.0

    @property
    def seconds(self) -> float:
        return self.frames / FPS

    @property
    def lines_remaining(self) -> int | None:
        return None if self.goal is None else max(0, self.goal - self.lines)

    def piece_cells(self, piece: ActivePiece | None = None, dx: int = 0, dy: int = 0,
                    rotation: int | None = None) -> list[tuple[int, int]]:
        piece = piece or self.piece
        rot = piece.rotation if rotation is None else rotation
        shape = self.system.shape(piece.kind, rot)
        return [(piece.x + dx + cx, piece.y + dy + cy) for cx, cy in shape]

    def drop_distance(self) -> int:
        distance = 0
        while self.board.fits(self.piece_cells(dy=distance + 1)):
            distance += 1
        return distance

    def ghost_cells(self) -> list[tuple[int, int]]:
        return self.piece_cells(dy=self.drop_distance())

    # --- bucle -----------------------------------------------------------------

    def update(self, held: set[str] | frozenset[str], pressed: set[str] | frozenset[str]) -> None:
        """Avanza un fotograma. `held` son las acciones mantenidas y `pressed`
        las que se acaban de pulsar en este fotograma."""
        self.events = []
        if self.finished:
            return
        self.frames += 1
        shift = self._das_step(held, pressed)

        if self.state == "are":
            self.timer -= 1
            if self.timer <= 0:
                self._spawn()
        elif self.state == "clearing":
            self.timer -= 1
            if self.timer <= 0:
                self._finish_clear()
        elif self.state == "falling":
            self._update_falling(held, pressed, shift)

    def _das_step(self, held, pressed) -> int:
        """Gestiona el autodesplazamiento (DAS). Se carga también entre piezas,
        como en el NES. Devuelve 0 = no mover, 1 = una casilla, 2 = hasta la pared."""
        if Action.LEFT in pressed:
            self._last_dir = -1
        if Action.RIGHT in pressed:
            self._last_dir = 1
        left, right = Action.LEFT in held, Action.RIGHT in held
        if left and right:
            direction = self._last_dir
        else:
            direction = -1 if left else 1 if right else 0

        if direction != self._das_dir:
            self._das_dir = direction
            self._das_counter = 0
            return 1 if direction else 0
        if not direction:
            return 0
        self._das_counter += 1
        if self._das_counter < self.rules.das:
            return 0
        if self.rules.arr <= 0:
            self._das_counter = self.rules.das
            return 2
        self._das_counter = self.rules.das - self.rules.arr
        return 1

    def _update_falling(self, held, pressed, shift: int) -> None:
        rules = self.rules
        if Action.HOLD in pressed and rules.hold and not self.hold_used:
            self._hold()
            if self.state != "falling":
                return

        if shift:
            moved = self._try_shift(self._das_dir)
            if shift == 2:
                while self._try_shift(self._das_dir):
                    pass
            if not moved:
                # Contra la pared el DAS queda cargado (comportamiento del NES).
                self._das_counter = rules.das

        if Action.ROTATE_CW in pressed:
            self._try_rotate(1)
        if Action.ROTATE_CCW in pressed:
            self._try_rotate(-1)

        if Action.HARD_DROP in pressed and rules.hard_drop:
            distance = self.drop_distance()
            self.piece.y += distance
            self.score += 2 * distance
            self.events.append("hard_drop")
            self._lock()
            return

        soft = Action.SOFT_DROP in held
        gravity = gravity_frames(self.level)
        if soft:
            gravity = min(gravity, rules.soft_drop_frames)
        self._gravity_counter += 1
        if self._gravity_counter >= gravity:
            self._gravity_counter = 0
            if self.board.fits(self.piece_cells(dy=1)):
                self.piece.y += 1
                if soft:
                    self.score += 1
                if self.piece.y > self._lowest_y:
                    self._lowest_y = self.piece.y
                    self._lock_timer = 0
                    self._lock_resets_used = 0

        if not self.board.fits(self.piece_cells(dy=1)):
            # Apoyada: se fija tras lo que tardaría en caer otra fila (como el NES)
            # o tras el margen mínimo `lock_delay`, lo que sea mayor. Así siempre hay
            # tiempo para colarla en un hueco, incluso bajando rápido o a nivel alto.
            self._lock_timer += 1
            if self._lock_timer >= max(gravity, rules.lock_delay):
                self._lock()

    # --- acciones --------------------------------------------------------------

    def _after_move(self) -> None:
        if self._lock_timer > 0 and self._lock_resets_used < self.rules.lock_resets:
            self._lock_timer = 0
            self._lock_resets_used += 1

    def _try_shift(self, direction: int) -> bool:
        if not direction or not self.board.fits(self.piece_cells(dx=direction)):
            return False
        self.piece.x += direction
        self.events.append("move")
        self._after_move()
        return True

    def _try_rotate(self, direction: int) -> bool:
        piece = self.piece
        states = self.system.states(piece.kind)
        if states == 1:
            return False
        target = (piece.rotation + direction) % states
        for kx, ky in self.system.kicks(piece.kind, piece.rotation, target):
            if self.board.fits(self.piece_cells(dx=kx, dy=ky, rotation=target)):
                piece.x += kx
                piece.y += ky
                piece.rotation = target
                self.events.append("rotate")
                self._after_move()
                return True
        return False

    def _hold(self) -> None:
        current = self.piece.kind
        self.hold_used = True
        self.events.append("hold")
        if self.held is None:
            self.held = current
            self._spawn()
        else:
            kind, self.held = self.held, current
            self._spawn(kind)

    def _spawn(self, kind: str | None = None) -> None:
        if kind is None:
            kind = self.queue.pop(0)
            self.queue.append(self.randomizer.next())
            self.stats[kind] += 1
        x, y = self.system.spawn_position(kind, self.board.hidden)
        self.piece = ActivePiece(kind, 0, x, y)
        self.state = "falling"
        self._gravity_counter = 0
        self._lock_timer = 0
        self._lock_resets_used = 0
        self._lowest_y = y
        if not self.board.fits(self.piece_cells()):
            self._end("over")

    def _lock(self) -> None:
        cells = self.piece_cells()
        self.board.place(cells, self.piece.kind)
        self.events.append("lock")
        self.hold_used = False
        self._lock_row = max(y for _, y in cells)
        self.piece = None
        full = self.board.full_rows()
        if full:
            self.clearing_rows = full
            self.events.append(f"clear{len(full)}")
            self.state = "clearing"
            self.timer = self.rules.line_clear_frames
            if self.timer <= 0:
                self._finish_clear()
        elif self._above_limit():
            self._end("over")
        else:
            self._begin_entry_delay()

    def _above_limit(self) -> bool:
        """¿Queda algún bloque por encima de la zona visible? Entonces se pierde,
        aunque solo sobresalga una parte de la pieza (p. ej. una I girada arriba)."""
        return any(c is not None for row in self.board.cells[: self.board.hidden] for c in row)

    def _finish_clear(self) -> None:
        count = len(self.clearing_rows)
        self.board.clear_rows(self.clearing_rows)
        self.clearing_rows = []
        self.score += LINE_SCORES[min(count, 4)] * (self.level + 1)
        self.lines += count
        if count == 4:
            self.tetris_lines += 4
        new_level = max(self.level, level_for_lines(self.rules.start_level, self.lines))
        if new_level > self.level:
            self.level = new_level
            self.events.append("level_up")
        if self.goal is not None and self.lines >= self.goal:
            self._end("won")
            return
        if self._above_limit():
            self._end("over")
            return
        self._begin_entry_delay()

    def _begin_entry_delay(self) -> None:
        if self.rules.entry_delay < 0:
            frames = nes_entry_delay(self.board.height - self._lock_row)
        else:
            frames = self.rules.entry_delay
        self.state = "are"
        self.timer = frames
        if frames <= 0:
            self._spawn()

    def _end(self, state: str) -> None:
        self.state = state
        self.events.append("game_over" if state == "over" else "won")
