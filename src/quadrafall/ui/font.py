# SPDX-License-Identifier: GPL-3.0-or-later
"""Fuente pixelada 5x7 propia (monoespaciada, estilo 8 bits) y fuente "lisa"
alternativa. Las minúsculas se dibujan como mayúsculas."""

from __future__ import annotations

import pygame

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


class PixelFont:
    """Dibuja texto con la fuente pixelada. `scale` = tamaño de cada píxel."""

    def __init__(self):
        self._cache: dict[tuple, pygame.Surface] = {}

    def line_height(self, scale: int) -> int:
        return (GLYPH_H + TOP) * scale

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return (max(0, len(text.upper()) * (GLYPH_W + 1) - 1) * scale, self.line_height(scale))

    def render(self, text: str, color, scale: int) -> pygame.Surface:
        text = text.upper()
        key = (text, tuple(color), scale)
        surf = self._cache.get(key)
        if surf is not None:
            return surf
        if len(self._cache) > 800:
            self._cache.clear()
        w, h = self.size(text, scale)
        surf = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
        for i, ch in enumerate(text):
            pixels = _GLYPHS.get(ch, _GLYPHS["?"])
            ox = i * (GLYPH_W + 1) * scale
            for x, y in pixels:
                surf.fill(color, (ox + x * scale, (y + TOP) * scale, scale, scale))
        self._cache[key] = surf
        return surf


class SmoothFont:
    """Alternativa con la fuente vectorial incluida en pygame. Las flechas, que esa
    fuente no trae, se dibujan con los glifos de la fuente pixelada."""

    PIXEL_ONLY = "←→↑↓"

    def __init__(self, pixel: PixelFont):
        self.pixel = pixel
        self._fonts: dict[int, pygame.font.Font] = {}
        self._cache: dict[tuple, pygame.Surface] = {}

    def _font(self, scale: int) -> pygame.font.Font:
        if scale not in self._fonts:
            self._fonts[scale] = pygame.font.Font(None, int(scale * 11))
        return self._fonts[scale]

    def line_height(self, scale: int) -> int:
        return (GLYPH_H + TOP) * scale

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return self.render(text, (0, 0, 0), scale).get_width(), self.line_height(scale)

    def _runs(self, text: str) -> list[tuple[bool, str]]:
        """Divide el texto en tramos (¿pixelado?, texto)."""
        runs: list[tuple[bool, str]] = []
        for ch in text:
            pixel = ch in self.PIXEL_ONLY
            if runs and runs[-1][0] == pixel:
                runs[-1] = (pixel, runs[-1][1] + ch)
            else:
                runs.append((pixel, ch))
        return runs

    def render(self, text: str, color, scale: int) -> pygame.Surface:
        key = (text, tuple(color), scale)
        surf = self._cache.get(key)
        if surf is None:
            if len(self._cache) > 800:
                self._cache.clear()
            height = self.line_height(scale)
            parts = [self.pixel.render(run, color, scale) if pixel else self._font(scale).render(run, True, color)
                     for pixel, run in self._runs(text)]
            gap = scale
            width = sum(p.get_width() for p in parts) + gap * max(0, len(parts) - 1)
            surf = pygame.Surface((max(1, width), height), pygame.SRCALPHA)
            x = 0
            for part in parts:
                surf.blit(part, (x, height - part.get_height()))
                x += part.get_width() + gap
            self._cache[key] = surf
        return surf


class Text:
    """Punto único para escribir texto; permite cambiar de fuente en caliente."""

    def __init__(self, kind: str = "pixel"):
        self.pixel = PixelFont()
        self.smooth: SmoothFont | None = None
        self.kind = kind

    @property
    def font(self):
        if self.kind == "smooth":
            if self.smooth is None:
                self.smooth = SmoothFont(self.pixel)
            return self.smooth
        return self.pixel

    def size(self, text: str, scale: int) -> tuple[int, int]:
        return self.font.size(text, scale)

    def draw(self, surface: pygame.Surface, text: str, pos, color, scale: int = 3,
             align: str = "left", shadow=None) -> pygame.Rect:
        surf = self.font.render(text, color, scale)
        rect = surf.get_rect()
        x, y = pos
        if align == "center":
            rect.midtop = (x, y)
        elif align == "right":
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        if shadow is not None:
            surface.blit(self.font.render(text, shadow, scale), rect.move(scale, scale))
        surface.blit(surf, rect)
        return rect
