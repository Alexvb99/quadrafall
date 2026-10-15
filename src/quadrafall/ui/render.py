# SPDX-License-Identifier: GPL-3.0-or-later
"""Dibujo del tablero, las piezas y los marcadores sobre una superficie de 1280x720."""

from __future__ import annotations

import pygame

from ..engine.pieces import PIECES, preview_shape
from ..i18n import t
from .font import Text
from .themes import Theme, darken, lighten, mix

W, H = 1280, 720
CELL = 30


def format_time(frames: int, precise: bool = False) -> str:
    total = frames / 60
    minutes, seconds = divmod(total, 60)
    if precise:
        return f"{int(minutes):02d}:{seconds:05.2f}"
    return f"{int(minutes):02d}:{int(seconds):02d}"


class Layout:
    """Posiciones de cada panel según las opciones activas."""

    def __init__(self, rules, visual: dict):
        self.board = pygame.Rect((W - 10 * CELL) // 2, 80, 10 * CELL, 20 * CELL)
        self.lines_box = pygame.Rect(self.board.x, 20, self.board.w, 44)
        left, right, width = 200, 830, 250
        y = self.board.y
        self.hold = None
        if rules.hold:
            self.hold = pygame.Rect(left, y, width, 130)
            y += 150
        self.stats = pygame.Rect(left, y, width, self.board.bottom - y) if visual["show_stats"] else None
        n = rules.next_count
        self.next = pygame.Rect(right, self.board.y, width, 40 + 90 + 60 * (n - 1)) if n else None
        info_y = self.next.bottom + 20 if self.next else self.board.y
        self.info = pygame.Rect(right, info_y, width, 190)
        self.mode_label = (left, 34)


class Renderer:
    def __init__(self, text: Text):
        self.text = text
        self._backgrounds: dict[str, pygame.Surface] = {}
        self._ghosts: dict[tuple, pygame.Surface] = {}
        self._crt: pygame.Surface | None = None

    # --- fondo y paneles ------------------------------------------------------

    def background(self, surf: pygame.Surface, theme: Theme) -> None:
        bg = self._backgrounds.get(theme.key)
        if bg is None:
            bg = pygame.Surface((W, H))
            for y in range(H):
                bg.fill(mix(theme.background, theme.background2, y / H), (0, y, W, 1))
            line = mix(theme.background, theme.background2, 0.5)
            if theme.pattern == "bricks":
                mortar = darken(theme.background2, 0.35)
                for row, y in enumerate(range(0, H, 24)):
                    bg.fill(mortar, (0, y, W, 2))
                    offset = 24 if row % 2 else 0
                    for x in range(-offset, W, 48):
                        bg.fill(mortar, (x, y, 2, 24))
            elif theme.pattern == "dots":
                dot = lighten(line, 0.12) if sum(theme.background) < 380 else darken(line, 0.08)
                for y in range(12, H, 24):
                    for x in range(12, W, 24):
                        bg.fill(dot, (x, y, 2, 2))
            elif theme.pattern == "stripes":
                stripe = darken(theme.background, 0.03)
                for x in range(-H, W, 40):
                    pygame.draw.line(bg, stripe, (x, H), (x + H, 0), 14)
            self._backgrounds[theme.key] = bg
        surf.blit(bg, (0, 0))

    def panel(self, surf, rect: pygame.Rect, theme: Theme, title: str | None = None) -> None:
        pygame.draw.rect(surf, theme.panel, rect, border_radius=6)
        if theme.panel_border:
            pygame.draw.rect(surf, theme.frame, rect, width=theme.panel_border, border_radius=6)
        if title:
            self.text.draw(surf, title, (rect.centerx, rect.y + 10), theme.text, 2, align="center")

    def crt(self, surf) -> None:
        if self._crt is None:
            self._crt = pygame.Surface((W, H), pygame.SRCALPHA)
            for y in range(0, H, 3):
                self._crt.fill((0, 0, 0, 70), (0, y, W, 1))
        surf.blit(self._crt, (0, 0))

    # --- bloques --------------------------------------------------------------

    def block(self, surf, x: int, y: int, size: int, kind: str, theme: Theme, style: str, level: int) -> None:
        fill, edge = theme.block_colors(kind, level, style)
        if style == "nes":
            gap = max(1, size // 8)
            r = pygame.Rect(x, y, size - gap, size - gap)
            s = max(1, round(size / 8))
            surf.fill(edge, r)
            if fill != edge:
                surf.fill(fill, r.inflate(-2 * s, -2 * s))
                surf.fill(theme.shine, (r.x, r.y, s, s))
            else:
                surf.fill(theme.shine, (r.x, r.y, s, s))
                surf.fill(theme.shine, (r.x + s, r.y + s, 2 * s, s))
                surf.fill(theme.shine, (r.x + s, r.y + 2 * s, s, s))
            return
        gap = max(1, size // 15)
        r = pygame.Rect(x, y, size - gap, size - gap)
        if style == "flat":
            surf.fill(fill, r)
        elif style == "bevel":
            b = max(2, size // 6)
            surf.fill(darken(fill, 0.4), r)
            pygame.draw.polygon(surf, lighten(fill, 0.45), [
                r.topleft, (r.right - 1, r.top), (r.right - 1 - b, r.top + b),
                (r.left + b, r.top + b), (r.left + b, r.bottom - 1 - b), (r.left, r.bottom - 1)])
            surf.fill(fill, r.inflate(-2 * b, -2 * b))
        elif style == "rounded":
            radius = max(2, size // 4)
            pygame.draw.rect(surf, darken(fill, 0.3), r, border_radius=radius)
            inner = r.inflate(-4, -4)
            pygame.draw.rect(surf, fill, inner, border_radius=radius - 1)
            pygame.draw.rect(surf, lighten(fill, 0.4),
                             (inner.x + 3, inner.y + 2, max(1, inner.w - 6), max(2, inner.h // 5)),
                             border_radius=2)
        else:  # outline
            surf.fill(darken(fill, 0.75), r)
            pygame.draw.rect(surf, fill, r, width=max(2, size // 8))
            surf.fill(fill, r.inflate(-size // 2, -size // 2))

    def ghost_block(self, surf, x: int, y: int, size: int, color) -> None:
        key = (size, tuple(color))
        ghost = self._ghosts.get(key)
        if ghost is None:
            ghost = pygame.Surface((size - 1, size - 1), pygame.SRCALPHA)
            ghost.fill((*color, 45))
            pygame.draw.rect(ghost, (*color, 170), ghost.get_rect(), width=2)
            self._ghosts[key] = ghost
        surf.blit(ghost, (x, y))

    def piece_icon(self, surf, kind: str, center, size: int, theme: Theme, style: str,
                   level: int, system: str) -> None:
        shape = preview_shape(kind, "srs" if system == "srs" else "nes")
        w = (max(x for x, _ in shape) + 1) * size
        h = (max(y for _, y in shape) + 1) * size
        ox, oy = center[0] - w // 2, center[1] - h // 2
        for x, y in shape:
            self.block(surf, ox + x * size, oy + y * size, size, kind, theme, style, level)

    # --- tablero --------------------------------------------------------------

    def board(self, surf, game, theme: Theme, visual: dict, rect: pygame.Rect, cell: int = CELL,
              hide_pieces: bool = False, curtain_rows: int = 0) -> None:
        board = game.board
        bg = theme.board
        if (game.state == "clearing" and len(game.clearing_rows) == 4 and visual["quad_flash"]
                and (game.timer // 4) % 2 == 0):
            bg = mix(theme.board, theme.text, 0.35)
        surf.fill(bg, rect)
        if visual["grid"]:
            for x in range(1, board.width):
                surf.fill(theme.grid, (rect.x + x * cell - 1, rect.y, 1, rect.h))
            for y in range(1, board.visible_height):
                surf.fill(theme.grid, (rect.x, rect.y + y * cell - 1, rect.w, 1))

        style = visual["block_style"]
        level = game.level
        if not hide_pieces:
            clearing = set(game.clearing_rows)
            progress = game.clear_progress
            anim = visual["clear_anim"]
            fade = None
            if clearing and anim == "fade":
                fade = pygame.Surface((cell, cell), pygame.SRCALPHA)
                fade.fill((*bg, int(255 * progress)))
            for y in range(board.hidden, board.height):
                sy = rect.y + (y - board.hidden) * cell
                for x, kind in enumerate(board.cells[y]):
                    if kind is None:
                        continue
                    sx = rect.x + x * cell
                    if y in clearing:
                        if anim == "nes":
                            step = int(progress * 5.999)
                            if abs(x - (board.width - 1) / 2) < step + 0.5:
                                continue
                        elif anim == "flash":
                            if int(progress * 8) % 2 == 0:
                                surf.fill(theme.text, (sx, sy, cell - 1, cell - 1))
                                continue
                            if progress > 0.75:
                                continue
                    self.block(surf, sx, sy, cell, kind, theme, style, level)
                    if fade is not None and y in clearing:
                        surf.blit(fade, (sx, sy))

            if game.piece is not None and game.state in ("falling", "over"):
                if visual["ghost"] and game.state == "falling":
                    color, _ = theme.block_colors(game.piece.kind, level, "flat")
                    for x, y in game.ghost_cells():
                        if y >= board.hidden:
                            self.ghost_block(surf, rect.x + x * cell, rect.y + (y - board.hidden) * cell, cell, color)
                for x, y in game.piece_cells():
                    if y >= board.hidden:
                        self.block(surf, rect.x + x * cell, rect.y + (y - board.hidden) * cell,
                                   cell, game.piece.kind, theme, style, level)

        for row in range(min(curtain_rows, board.visible_height)):
            sy = rect.y + row * cell
            surf.fill(darken(theme.frame, 0.2), (rect.x, sy, rect.w, cell - 2))
            surf.fill(lighten(theme.frame, 0.3), (rect.x, sy, rect.w, 3))

        if theme.frame_width >= 3:
            pygame.draw.rect(surf, theme.frame, rect.inflate(12, 12), width=theme.frame_width, border_radius=4)
            pygame.draw.rect(surf, darken(theme.frame, 0.5), rect.inflate(4, 4), width=2)
        elif theme.frame_width > 0:
            pygame.draw.rect(surf, theme.frame, rect.inflate(8, 8), width=theme.frame_width)

    # --- marcadores -----------------------------------------------------------

    def hud(self, surf, game, layout: Layout, theme: Theme, visual: dict, best: int, mode_name: str) -> None:
        txt = self.text
        style = visual["block_style"]
        level = game.level
        system = game.rules.rotation
        txt.draw(surf, mode_name, layout.mode_label, theme.text_dim, 2)

        # Líneas (o líneas restantes) encima del tablero
        box = layout.lines_box
        self.panel(surf, box, theme)
        if game.goal is None:
            label, value = t("lines"), f"{game.lines:03d}"
        else:
            label, value = t("lines_left"), f"{game.lines_remaining:02d}"
        txt.draw(surf, f"{label} {value}", (box.centerx, box.y + 9), theme.text, 3, align="center")

        if layout.hold:
            box = layout.hold
            self.panel(surf, box, theme, t("hold"))
            if game.held:
                self.piece_icon(surf, game.held, (box.centerx, box.y + 78), 26, theme, style, level, system)
                if game.hold_used:
                    veil = pygame.Surface((box.w - 12, box.h - 44), pygame.SRCALPHA)
                    veil.fill((*theme.panel, 170))
                    surf.blit(veil, (box.x + 6, box.y + 38))

        if layout.next:
            box = layout.next
            self.panel(surf, box, theme, t("next"))
            for i, kind in enumerate(game.preview):
                if i == 0:
                    self.piece_icon(surf, kind, (box.centerx, box.y + 40 + 45), 26, theme, style, level, system)
                else:
                    cy = box.y + 40 + 90 + (i - 1) * 60 + 26
                    self.piece_icon(surf, kind, (box.centerx, cy), 20, theme, style, level, system)

        if layout.stats:
            box = layout.stats
            self.panel(surf, box, theme, t("statistics"))
            row_h = min(64, (box.h - 44) // len(PIECES))
            order = ("T", "J", "Z", "O", "S", "L", "I")  # orden del NES
            for i, kind in enumerate(order):
                cy = box.y + 40 + i * row_h + row_h // 2
                self.piece_icon(surf, kind, (box.x + 70, cy), 15, theme, style, level, system)
                txt.draw(surf, f"{game.stats[kind]:03d}", (box.right - 24, cy - 15), theme.accent, 3, align="right")

        box = layout.info
        self.panel(surf, box, theme)
        rows = [
            (t("top"), f"{max(best, game.score):06d}"),
            (t("score"), f"{game.score:06d}"),
            (t("level"), f"{game.level:02d}"),
            (t("time"), format_time(game.frames, precise=game.rules.mode == "sprint")),
            (t("quads"), f"{round(game.tetris_rate * 100)}%"),
        ]
        for i, (label, value) in enumerate(rows):
            y = box.y + 14 + i * 34
            txt.draw(surf, label, (box.x + 16, y + 6), theme.text_dim, 2)
            txt.draw(surf, value, (box.right - 16, y), theme.text, 3, align="right")
