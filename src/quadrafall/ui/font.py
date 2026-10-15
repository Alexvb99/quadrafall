# SPDX-License-Identifier: GPL-3.0-or-later
"""Fuentes del juego.

- "pixel" (por defecto): VT323, de terminal con píxel fino, siempre en mayúsculas.
- "rounded": Varela Round, geométrica de esquinas redondeadas.
- "smooth": la fuente vectorial que trae pygame.

VT323 y Varela Round están en assets/fonts con la licencia SIL OFL 1.1. Los glifos
5x7 dibujados a mano de este archivo solo cubren lo que esas fuentes no traen.
"""

from __future__ import annotations

import pygame

from ..paths import asset_path

_GLYPHS_SRC = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.",
    "J": "..###|...#.|...#.|...#.|#..#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "#####|...#.|..#..|...#.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    " ": ".....|.....|.....|.....|.....|.....|.....",
    ".": ".....|.....|.....|.....|.....|.##..|.##..",
    ",": ".....|.....|.....|.....|.##..|..#..|.#...",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    ";": ".....|.##..|.##..|.....|.##..|..#..|.#...",
    "-": ".....|.....|.....|.###.|.....|.....|.....",
    "_": ".....|.....|.....|.....|.....|.....|#####",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "=": ".....|.....|#####|.....|#####|.....|.....",
    "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "¡": "..#..|.....|..#..|..#..|..#..|..#..|..#..",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "¿": "..#..|.....|..#..|.#...|#....|#...#|.###.",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    "%": "##..#|##..#|...#.|..#..|.#...|#..##|#..##",
    "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...",
    "[": ".###.|.#...|.#...|.#...|.#...|.#...|.###.",
    "]": ".###.|...#.|...#.|...#.|...#.|...#.|.###.",
    "'": "..#..|..#..|.#...|.....|.....|.....|.....",
    '"': ".#.#.|.#.#.|.....|.....|.....|.....|.....",
    "<": "...#.|..#..|.#...|#....|.#...|..#..|...#.",
    ">": ".#...|..#..|...#.|....#|...#.|..#..|.#...",
    "#": ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#.",
    "*": ".....|#.#.#|.###.|#####|.###.|#.#.#|.....",
    "·": ".....|.....|.....|..#..|.....|.....|.....",
    "←": ".....|..#..|.#...|#####|.#...|..#..|.....",
    "→": ".....|..#..|...#.|#####|...#.|..#..|.....",
    "↑": "..#..|.###.|#.#.#|..#..|..#..|..#..|.....",
    "↓": "..#..|..#..|..#..|#.#.#|.###.|..#..|.....",
    "×": ".....|#...#|.#.#.|..#..|.#.#.|#...#|.....",
}

# Diacríticos: se dibujan por encima de la letra base (filas -3 y -2).
_ACCENTS = {
    "acute": ("...#.", "..#.."),
    "tilde": (".##.#", "#.##."),
    "diaeresis": (".....", ".#.#."),
    "grave": (".#...", "..#.."),
}
_COMPOSED = {
    "Á": ("A", "acute"), "É": ("E", "acute"), "Í": ("I", "acute"),
    "Ó": ("O", "acute"), "Ú": ("U", "acute"), "Ñ": ("N", "tilde"),
    "Ü": ("U", "diaeresis"), "À": ("A", "grave"), "È": ("E", "grave"),
    "Ò": ("O", "grave"), "Ç": ("C", None),
}

GLYPH_W, GLYPH_H, TOP = 5, 7, 3   # TOP = filas reservadas para acentos


def _parse(src: str) -> list[tuple[int, int]]:
    return [(x, y) for y, row in enumerate(src.split("|")) for x, ch in enumerate(row) if ch == "#"]


_GLYPHS: dict[str, list[tuple[int, int]]] = {ch: _parse(src) for ch, src in _GLYPHS_SRC.items()}
for _char, (_base, _accent) in _COMPOSED.items():
    _pixels = list(_GLYPHS[_base])
    if _accent:
        for _row, _line in enumerate(_ACCENTS[_accent]):
            _pixels += [(x, _row - TOP) for x, ch in enumerate(_line) if ch == "#"]
    _GLYPHS[_char] = _pixels




class BitmapFont:
    """Los glifos 5x7 de arriba. Ya no es una fuente elegible: solo rellena los
    caracteres que no traen las fuentes TTF (las flechas). `scale` = tamaño del píxel."""

    def __init__(self):
        self._cache: dict[tuple, pygame.Surface] = {}

    def render(self, text: str, color, scale: int) -> pygame.Surface:
        """Superficie de alto 7*scale, con la base de las letras en el borde inferior."""
        text = text.upper()
        key = (text, tuple(color), scale)
        surf = self._cache.get(key)
        if surf is None:
            if len(self._cache) > 400:
                self._cache.clear()
            width = max(1, (len(text) * (GLYPH_W + 1) - 1) * scale)
            surf = pygame.Surface((width, GLYPH_H * scale), pygame.SRCALPHA)
            for i, ch in enumerate(text):
                ox = i * (GLYPH_W + 1) * scale
                for x, y in _GLYPHS.get(ch, _GLYPHS["?"]):
                    if y >= 0:
                        surf.fill(color, (ox + x * scale, y * scale, scale, scale))
            self._cache[key] = surf
        return surf


# Fuentes elegibles: archivo en assets/fonts (None = la de pygame), píxeles de
# tamaño por unidad de escala, suavizado, si se escribe en mayúsculas y tamaño
# nativo. Con tamaño nativo la fuente se rasteriza siempre a ese tamaño (donde sus
# píxeles salen limpios) y luego se amplía sin suavizar, para que ninguna letra se
# deforme a tamaños intermedios.
FONTS = {
    "pixel": ("VT323-Regular.ttf", 10.0, False, True, 20),          # terminal de píxel fino
    "rounded": ("VarelaRound-Regular.ttf", 10.0, True, False, None),  # geométrica redondeada
    "smooth": (None, 11.0, True, False, None),
}


class TTFont:
    """Texto con una fuente TTF dentro de una caja de alto 10*scale, con la línea
    base a la misma altura en todas las fuentes. Los caracteres que falten en la
    fuente se dibujan con BitmapFont."""

    def __init__(self, path: str | None, px_per_scale: float, antialias: bool, uppercase: bool,
                 native_size: int | None, fallback: BitmapFont):
        self.path = path
        self.px_per_scale = px_per_scale
        self.antialias = antialias
        self.uppercase = uppercase
        self.native_size = native_size
        self.fallback = fallback
        self._fonts: dict[int, pygame.font.Font] = {}
        self._cache: dict[tuple, pygame.Surface] = {}
        self._present: dict[str, bool] = {}
        self._missing_raw: bytes | None = None

    def _load(self, size: int) -> pygame.font.Font:
        font = self._fonts.get(size)
        if font is None:
            try:
                font = pygame.font.Font(self.path, size)
            except (OSError, pygame.error):
                font = pygame.font.Font(None, size)   # archivo ausente: fuente de pygame
            self._fonts[size] = font
        return font

    def _font(self, scale: int) -> tuple[pygame.font.Font, float]:
        """Fuente con la que se rasteriza y factor de ampliación posterior."""
        target = max(8.0, self.px_per_scale * scale)
        if self.native_size:
            return self._load(self.native_size), target / self.native_size
        return self._load(round(target)), 1.0

    def _metric(self, scale: int, name: str) -> int:
        font, factor = self._font(scale)
        return round(getattr(font, name)() * factor)

    def _has_glyph(self, ch: str) -> bool:
        if ch.isspace():
            return True
        present = self._present.get(ch)
        if present is None:
            font, _ = self._font(3)

            def raw(c: str) -> bytes:
                return pygame.image.tobytes(font.render(c, False, (255, 255, 255), (0, 0, 0)), "RGB")

            if self._missing_raw is None:
                self._missing_raw = raw("\ue000")   # glifo de "carácter ausente"
            present = raw(ch) != self._missing_raw
            self._present[ch] = present
        return present

    def _runs(self, text: str) -> list[tuple[bool, str]]:
        """Divide el texto en tramos (¿falta en la fuente?, texto)."""
        runs: list[tuple[bool, str]] = []
        for ch in text:
            missing = not self._has_glyph(ch)
            if runs and runs[-1][0] == missing:
                runs[-1] = (missing, runs[-1][1] + ch)
            else:
                runs.append((missing, ch))
        return runs

    def line_height(self, scale: int) -> int:
        return (GLYPH_H + TOP) * scale

    def _fallback_scale(self, scale: int) -> int:
        return max(1, round(self._metric(scale, "get_height") / 14))

    def _baseline(self, scale: int) -> int:
        return self.line_height(scale) + self._metric(scale, "get_descent")   # descent es negativo

    def top_pad(self, scale: int) -> int:
        """Píxeles que la superficie sobresale por encima de la caja (acentos altos)."""
        baseline = self._baseline(scale)
        return max(0, self._metric(scale, "get_ascent") - baseline,
                   GLYPH_H * self._fallback_scale(scale) - baseline)

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return self.render(text, (0, 0, 0), scale).get_width(), self.line_height(scale)

    def _render_run(self, run: str, color, scale: int) -> pygame.Surface:
        font, factor = self._font(scale)
        surf = font.render(run, self.antialias, color)
        if factor != 1.0:
            size = (max(1, round(surf.get_width() * factor)), max(1, round(surf.get_height() * factor)))
            surf = pygame.transform.scale(surf, size)
        return surf

    def render(self, text: str, color, scale: int) -> pygame.Surface:
        if self.uppercase:
            text = text.upper()
        key = (text, tuple(color), scale)
        surf = self._cache.get(key)
        if surf is None:
            if len(self._cache) > 800:
                self._cache.clear()
            baseline = self._baseline(scale)
            ascent = self._metric(scale, "get_ascent")
            pad = self.top_pad(scale)
            fallback_scale = self._fallback_scale(scale)
            parts = []
            for missing, run in self._runs(text):
                if missing:
                    part = self.fallback.render(run, color, fallback_scale)
                    parts.append((part, baseline - part.get_height()))
                else:
                    parts.append((self._render_run(run, color, scale), baseline - ascent))
            gap = fallback_scale
            width = sum(p.get_width() for p, _ in parts) + gap * max(0, len(parts) - 1)
            surf = pygame.Surface((max(1, width), self.line_height(scale) + pad), pygame.SRCALPHA)
            x = 0
            for part, top in parts:
                surf.blit(part, (x, top + pad))
                x += part.get_width() + gap
            self._cache[key] = surf
        return surf


class Text:
    """Punto único para escribir texto; permite cambiar de fuente en caliente."""

    def __init__(self, kind: str = "pixel"):
        self.fallback = BitmapFont()
        self._fonts: dict[str, TTFont] = {}
        self.kind = kind

    @property
    def font(self) -> TTFont:
        kind = self.kind if self.kind in FONTS else "pixel"
        if kind not in self._fonts:
            filename, px_per_scale, antialias, uppercase, native = FONTS[kind]
            path = str(asset_path("fonts/" + filename)) if filename else None
            self._fonts[kind] = TTFont(path, px_per_scale, antialias, uppercase, native, self.fallback)
        return self._fonts[kind]

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return self.font.size(text, scale)

    def draw(self, surface: pygame.Surface, text: str, pos, color, scale: int = 3,
             align: str = "left", shadow=None) -> pygame.Rect:
        font = self.font
        surf = font.render(text, color, scale)
        rect = surf.get_rect()
        x, y = pos[0], pos[1] - font.top_pad(scale)
        if align == "center":
            rect.midtop = (x, y)
        elif align == "right":
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        if shadow is not None:
            offset = max(1, scale // 2 + 1)
            surface.blit(font.render(text, shadow, scale), rect.move(offset, offset))
        surface.blit(surf, rect)
        return rect
