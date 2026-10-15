# SPDX-License-Identifier: GPL-3.0-or-later
"""Temas de color y estilos de bloque. Añadir un tema nuevo = añadir una entrada a THEMES."""

from __future__ import annotations

from dataclasses import dataclass, field

Color = tuple[int, int, int]


def lighten(c: Color, amount: float) -> Color:
    return tuple(int(v + (255 - v) * amount) for v in c)


def darken(c: Color, amount: float) -> Color:
    return tuple(int(v * (1 - amount)) for v in c)


def mix(a: Color, b: Color, t: float) -> Color:
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


# Paletas del NES por nivel (se repiten cada 10 niveles): (color 1, color 2).
NES_LEVEL_COLORS: list[tuple[Color, Color]] = [
    ((0, 88, 248), (60, 188, 252)),     # 0 azul / celeste
    ((0, 168, 0), (184, 248, 24)),      # 1 verdes
    ((216, 0, 204), (248, 120, 248)),   # 2 morado / rosa
    ((0, 88, 248), (88, 216, 84)),      # 3 azul / verde
    ((228, 0, 88), (88, 248, 152)),     # 4 magenta / menta
    ((88, 248, 152), (104, 136, 252)),  # 5 menta / lavanda
    ((248, 56, 0), (124, 124, 124)),    # 6 rojo / gris
    ((104, 68, 252), (168, 0, 32)),     # 7 violeta / granate
    ((0, 88, 248), (248, 56, 0)),       # 8 azul / rojo
    ((248, 56, 0), (252, 160, 68)),     # 9 rojo / naranja
]


@dataclass(frozen=True)
class Theme:
    key: str
    background: Color
    background2: Color          # parte baja del degradado
    board: Color
    grid: Color
    frame: Color
    panel: Color
    text: Color
    text_dim: Color
    accent: Color
    pieces: dict[str, Color] = field(default_factory=dict)
    nes_levels: bool = False    # colores que cambian con el nivel, como el NES
    pattern: str | None = None  # "bricks", "dots", "stripes" o None
    default_style: str = "bevel"
    default_font: str = "pixel"
    shine: Color = (252, 252, 252)
    panel_border: int = 3       # grosor del borde de los paneles (0 = sin borde)
    frame_width: int = 4        # grosor del marco del tablero
    ornaments: bool = True      # sombras en títulos y piezas decorativas en el menú

    def shadow(self, amount: float = 0.5) -> Color | None:
        """Color de la sombra de los títulos, o None si el tema no usa sombras."""
        return darken(self.background2, amount) if self.ornaments else None

    def block_colors(self, kind: str, level: int, style: str) -> tuple[Color, Color]:
        """(relleno, borde) de un bloque. Con el tema NES, T/O/I son bloques
        blancos con borde de color y el resto usa los dos colores del nivel."""
        if self.nes_levels:
            c1, c2 = NES_LEVEL_COLORS[level % 10]
            if kind in "TOI":
                return ((252, 252, 252), c1) if style == "nes" else (lighten(c1, 0.55), c1)
            color = c1 if kind in "JS" else c2
            return color, color
        color = self.pieces.get(kind, self.text)
        return color, color


THEMES: dict[str, Theme] = {
    "nes": Theme(
        key="nes", background=(52, 52, 64), background2=(28, 28, 36), board=(0, 0, 0),
        grid=(22, 22, 30), frame=(124, 124, 124), panel=(0, 0, 0), text=(252, 252, 252),
        text_dim=(168, 168, 180), accent=(252, 160, 68), nes_levels=True, pattern="bricks",
        default_style="nes",
    ),
    "classic": Theme(  # inspirado en la paleta Tango que usa Quadrapassel
        key="classic", background=(46, 52, 54), background2=(26, 30, 31), board=(20, 22, 23),
        grid=(38, 42, 44), frame=(136, 138, 133), panel=(20, 22, 23), text=(238, 238, 236),
        text_dim=(186, 189, 182), accent=(252, 175, 62), default_style="bevel",
        pieces={"I": (239, 41, 41), "O": (114, 159, 207), "T": (186, 189, 182),
                "S": (173, 127, 168), "Z": (138, 226, 52), "J": (252, 233, 79), "L": (252, 175, 62)},
    ),
    "modern": Theme(
        key="modern", background=(24, 26, 48), background2=(8, 8, 20), board=(10, 10, 22),
        grid=(30, 32, 56), frame=(90, 96, 160), panel=(14, 14, 30), text=(240, 240, 255),
        text_dim=(150, 155, 200), accent=(0, 230, 230), pattern="dots", default_style="rounded",
        pieces={"I": (0, 230, 240), "O": (245, 225, 0), "T": (170, 50, 240), "S": (40, 220, 60),
                "Z": (240, 40, 50), "J": (40, 90, 245), "L": (245, 150, 20)},
    ),
    "gameboy": Theme(
        key="gameboy", background=(139, 172, 15), background2=(110, 145, 12), board=(155, 188, 15),
        grid=(145, 178, 15), frame=(15, 56, 15), panel=(155, 188, 15), text=(15, 56, 15),
        text_dim=(48, 98, 48), accent=(15, 56, 15), pattern="dots", default_style="nes",
        shine=(139, 172, 15),
        pieces={"I": (15, 56, 15), "O": (48, 98, 48), "T": (15, 56, 15), "S": (48, 98, 48),
                "Z": (15, 56, 15), "J": (48, 98, 48), "L": (15, 56, 15)},
    ),
    "pastel": Theme(
        key="pastel", background=(250, 240, 245), background2=(225, 230, 250), board=(255, 252, 250),
        grid=(236, 230, 236), frame=(190, 170, 200), panel=(255, 252, 250), text=(80, 60, 90),
        text_dim=(140, 120, 150), accent=(230, 120, 160), pattern="stripes", default_style="rounded",
        pieces={"I": (130, 210, 230), "O": (250, 220, 120), "T": (200, 160, 230), "S": (150, 220, 150),
                "Z": (245, 150, 150), "J": (140, 170, 240), "L": (250, 180, 120)},
    ),
    "minimal": Theme(  # liso, en grises, sin bordes ni adornos
        key="minimal", background=(246, 246, 244), background2=(246, 246, 244), board=(246, 246, 244),
        grid=(238, 238, 236), frame=(205, 205, 202), panel=(246, 246, 244), text=(40, 40, 40),
        text_dim=(150, 150, 148), accent=(40, 40, 40), default_style="flat", default_font="smooth",
        panel_border=0, frame_width=1, ornaments=False,
        pieces={"I": (45, 45, 45), "O": (150, 150, 150), "T": (85, 85, 85), "S": (120, 120, 120),
                "Z": (100, 100, 100), "J": (65, 65, 65), "L": (135, 135, 135)},
    ),
    "colorblind": Theme(  # paleta Okabe-Ito, distinguible con daltonismo
        key="colorblind", background=(30, 30, 30), background2=(12, 12, 12), board=(0, 0, 0),
        grid=(40, 40, 40), frame=(200, 200, 200), panel=(0, 0, 0), text=(255, 255, 255),
        text_dim=(190, 190, 190), accent=(240, 228, 66), default_style="outline",
        pieces={"I": (86, 180, 233), "O": (240, 228, 66), "T": (204, 121, 167), "S": (0, 158, 115),
                "Z": (213, 94, 0), "J": (0, 114, 178), "L": (230, 159, 0)},
    ),
}

BLOCK_STYLES = ("nes", "bevel", "flat", "rounded", "outline")
CLEAR_ANIMATIONS = ("nes", "flash", "fade")
