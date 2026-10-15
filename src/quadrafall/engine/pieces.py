# SPDX-License-Identifier: GPL-3.0-or-later
"""Definición de piezas y sistemas de rotación.

Coordenadas: x crece hacia la derecha, y crece hacia abajo (fila 0 = arriba).
Cada forma es una lista de celdas (dx, dy) relativas a la posición de la pieza.

Sistemas disponibles:
- "nes":      Nintendo Rotation System. Rota alrededor de un pivote, sin patadas
              (si no cabe, no rota). S, Z e I solo tienen dos orientaciones.
- "nes_plus": las mismas formas que NES, con patadas sencillas contra paredes
              y suelo. Una "mejora moderna ligera".
- "srs":      Super Rotation System (el de los juegos modernos), con su tabla
              de patadas oficial.
"""

from __future__ import annotations

PIECES = ("I", "O", "T", "S", "Z", "J", "L")
# Orden en el que el NES enumera las piezas (lo usa su generador aleatorio).
NES_ORDER = ("T", "J", "Z", "O", "S", "L", "I")

Cell = tuple[int, int]
Shape = tuple[Cell, ...]


def _rotate_about_origin(shape: Shape) -> Shape:
    """Gira 90° en sentido horario (con y hacia abajo): (x, y) -> (-y, x)."""
    return tuple((-y, x) for x, y in shape)


def _rotate_in_box(shape: Shape, size: int) -> Shape:
    """Gira 90° en sentido horario dentro de una caja size x size."""
    return tuple((size - 1 - y, x) for x, y in shape)


def _all_rotations(first: Shape, rotate) -> tuple[Shape, ...]:
    states = [first]
    for _ in range(3):
        states.append(rotate(states[-1]))
    return tuple(states)


# --- NES (pivote en (0, 0), estado 0 = orientación de aparición) -------------

_NES_SHAPES: dict[str, tuple[Shape, ...]] = {
    "T": _all_rotations(((-1, 0), (0, 0), (1, 0), (0, 1)), _rotate_about_origin),
    "J": _all_rotations(((-1, 0), (0, 0), (1, 0), (1, 1)), _rotate_about_origin),
    "L": _all_rotations(((-1, 0), (0, 0), (1, 0), (-1, 1)), _rotate_about_origin),
    "S": (((0, 0), (1, 0), (-1, 1), (0, 1)), ((0, -1), (0, 0), (1, 0), (1, 1))),
    "Z": (((-1, 0), (0, 0), (0, 1), (1, 1)), ((1, -1), (0, 0), (1, 0), (0, 1))),
    "I": (((-2, 0), (-1, 0), (0, 0), (1, 0)), ((0, -2), (0, -1), (0, 0), (0, 1))),
    "O": (((-1, 0), (0, 0), (-1, 1), (0, 1)),),
}

# --- SRS (posición = esquina superior izquierda de la caja) ------------------

_SRS_SHAPES: dict[str, tuple[Shape, ...]] = {
    "I": _all_rotations(((0, 1), (1, 1), (2, 1), (3, 1)), lambda s: _rotate_in_box(s, 4)),
    "O": (((1, 0), (2, 0), (1, 1), (2, 1)),),
    "T": _all_rotations(((1, 0), (0, 1), (1, 1), (2, 1)), lambda s: _rotate_in_box(s, 3)),
    "J": _all_rotations(((0, 0), (0, 1), (1, 1), (2, 1)), lambda s: _rotate_in_box(s, 3)),
    "L": _all_rotations(((2, 0), (0, 1), (1, 1), (2, 1)), lambda s: _rotate_in_box(s, 3)),
    "S": _all_rotations(((1, 0), (2, 0), (0, 1), (1, 1)), lambda s: _rotate_in_box(s, 3)),
    "Z": _all_rotations(((0, 0), (1, 0), (1, 1), (2, 1)), lambda s: _rotate_in_box(s, 3)),
}


def _flip_y(table: dict[tuple[int, int], tuple[Cell, ...]]) -> dict[tuple[int, int], tuple[Cell, ...]]:
    # Las tablas SRS se publican con y hacia arriba; aquí y crece hacia abajo.
    return {k: tuple((x, -y) for x, y in v) for k, v in table.items()}


_SRS_KICKS_JLSTZ = _flip_y({
    (0, 1): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    (1, 0): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    (1, 2): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    (2, 1): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    (2, 3): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    (3, 2): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    (3, 0): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    (0, 3): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
})

_SRS_KICKS_I = _flip_y({
    (0, 1): ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
    (1, 0): ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
    (1, 2): ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)),
    (2, 1): ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
    (2, 3): ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
    (3, 2): ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
    (3, 0): ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
    (0, 3): ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)),
})

_NO_KICKS: tuple[Cell, ...] = ((0, 0),)
# Patadas sencillas: sitio, izquierda, derecha y un escalón hacia arriba.
_SIMPLE_KICKS: tuple[Cell, ...] = ((0, 0), (-1, 0), (1, 0), (0, -1))
_SIMPLE_KICKS_I: tuple[Cell, ...] = ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1))


class RotationSystem:
    def __init__(self, name: str, shapes: dict[str, tuple[Shape, ...]], spawn_x: int):
        self.name = name
        self.shapes = shapes
        self.spawn_x = spawn_x

    def states(self, kind: str) -> int:
        return len(self.shapes[kind])

    def shape(self, kind: str, rotation: int) -> Shape:
        states = self.shapes[kind]
        return states[rotation % len(states)]

    def kicks(self, kind: str, start: int, end: int) -> tuple[Cell, ...]:
        if self.name == "srs":
            if kind == "O":
                return _NO_KICKS
            table = _SRS_KICKS_I if kind == "I" else _SRS_KICKS_JLSTZ
            return table[(start % 4, end % 4)]
        if self.name == "nes_plus":
            return _SIMPLE_KICKS_I if kind == "I" else _SIMPLE_KICKS
        return _NO_KICKS

    def spawn_position(self, kind: str, top_row: int) -> tuple[int, int]:
        """Posición de aparición: la celda más alta de la pieza queda en top_row."""
        min_dy = min(dy for _, dy in self.shape(kind, 0))
        return self.spawn_x, top_row - min_dy


ROTATION_SYSTEMS = {
    "nes": RotationSystem("nes", _NES_SHAPES, spawn_x=5),
    "nes_plus": RotationSystem("nes_plus", _NES_SHAPES, spawn_x=5),
    "srs": RotationSystem("srs", _SRS_SHAPES, spawn_x=3),
}


def preview_shape(kind: str, system: str = "srs") -> Shape:
    """Forma de aparición normalizada (esquina en 0,0) para dibujarla en paneles."""
    shape = ROTATION_SYSTEMS[system].shape(kind, 0)
    min_x = min(x for x, _ in shape)
    min_y = min(y for _, y in shape)
    return tuple((x - min_x, y - min_y) for x, y in shape)
