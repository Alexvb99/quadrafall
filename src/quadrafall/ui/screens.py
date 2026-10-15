# SPDX-License-Identifier: GPL-3.0-or-later
"""Pantallas de menú: título, opciones, controles, récords y nombre."""

from __future__ import annotations

import random

import pygame

from .. import __version__, APP_NAME
from ..engine.game import MODES, Action, ActivePiece, Game, GameRules
from ..engine.pieces import PIECES
from ..i18n import set_language, t
from .input import ACTION_LABELS, binding_label, event_to_binding
from .menu import (NAV_ACCEPT, NAV_BACK, NAV_DELETE, NAV_DOWN, NAV_LEFT, NAV_RIGHT, NAV_UP, Choice,
                   Item, MenuScene, NavReader, Range, Scene, Toggle)
from .play import MODE_LABELS, GameScene
from .render import H, W, format_time
from .themes import BLOCK_STYLES, CLEAR_ANIMATIONS, THEMES


def _frames(v: int) -> str:
    return t("frames", n=v)


# --- título -------------------------------------------------------------------

class TitleScene(MenuScene):
    def __init__(self, app):
        s = app.settings
        super().__init__(app, [
            Item("play", self._play),
            Choice("mode", [(m, MODE_LABELS[m]) for m in MODES],
                   lambda: s.rules["mode"], lambda v: s.rules.__setitem__("mode", v)),
            Range("start_level", 0, 19, lambda: s.rules["start_level"],
                  lambda v: s.rules.__setitem__("start_level", v)),
            Range("garbage_rows", 0, 12, lambda: s.rules["garbage_rows"],
                  lambda v: s.rules.__setitem__("garbage_rows", v), help_key="help_garbage"),
            Item("options", lambda: app.push(OptionsScene(app))),
            Item("controls", lambda: app.push(ControlsScene(app))),
            Item("highscores", lambda: app.push(ScoresScene(app, s.rules["mode"]))),
            Item("quit", app.quit),
        ])
        self.area = pygame.Rect(W // 2 - 260, 260, 520, 8 * self.row_h)
        self.rng = random.Random()
        self.falling = [self._new_piece(initial=True) for _ in range(12)]
        self.frame = 0

    def _new_piece(self, initial: bool = False) -> list:
        side = self.rng.random() < 0.5
        x = self.rng.randrange(30, 300) if side else self.rng.randrange(W - 300, W - 60)
        y = self.rng.randrange(-H, H) if initial else self.rng.randrange(-200, -60)
        return [self.rng.choice(PIECES), x, y, self.rng.uniform(0.4, 1.4)]

    def _play(self) -> None:
        self.app.settings.save()
        self.app.push(GameScene(self.app))

    def on_back(self) -> None:
        self.selected = len(self.items) - 1   # ESC en el título lleva a "Salir"

    def on_change(self, item) -> None:
        self.app.settings.save()

    def update(self) -> None:
        self.frame += 1
        for piece in self.falling:
            piece[2] += piece[3]
        self.falling = [p if p[2] < H + 60 else self._new_piece() for p in self.falling]

    def draw(self, surf) -> None:
        app = self.app
        theme, txt, visual = app.theme, app.text, app.settings.visual
        self.draw_background(surf)
        for kind, x, y, _ in (self.falling if theme.ornaments else []):
            app.renderer.piece_icon(surf, kind, (x, int(y)), 22, theme, visual["block_style"],
                                    (self.frame // 600) % 10, "srs")
        # Logo con cada letra del color de una pieza
        title = APP_NAME.upper()
        scale = 9
        width = txt.size(title, scale)[0]
        x = W // 2 - width // 2
        for i, ch in enumerate(title):
            color, _ = theme.block_colors(PIECES[i % len(PIECES)], (self.frame // 600) % 10, "flat")
            rect = txt.draw(surf, ch, (x, 60), color, scale, shadow=theme.shadow(0.6))
            x = rect.right + scale
        txt.draw(surf, t("subtitle"), (W // 2, 180), theme.text_dim, 2, align="center")
        self.draw_items(surf)
        self.draw_help(surf)
        txt.draw(surf, f"v{__version__} · GPL-3.0+", (W - 20, H - 26), theme.text_dim, 2, align="right")


# --- opciones -----------------------------------------------------------------

class OptionsSubScene(MenuScene):
    def leave(self) -> None:
        self.app.settings.save()
        self.app.apply_settings()


class OptionsScene(OptionsSubScene):
    title_key = "options"

    def __init__(self, app):
        s = app.settings

        def set_lang(code):
            s.data["language"] = code
            set_language(code)

        super().__init__(app, [
            Item("gameplay", lambda: app.push(GameplayScene(app))),
            Item("appearance", lambda: app.push(AppearanceScene(app))),
            Item("sound", lambda: app.push(SoundScene(app))),
            Item("controls", lambda: app.push(ControlsScene(app))),
            Choice("language", [("auto", "lang_auto"), ("es", "lang_es"), ("en", "lang_en")],
                   lambda: s.data["language"], set_lang),
            Toggle("fullscreen", lambda: s.visual["fullscreen"], app.set_fullscreen),
            Item("back", app.pop),
        ])
        self.area = pygame.Rect(W // 2 - 380, 160, 760, len(self.items) * self.row_h)


class GameplayScene(OptionsSubScene):
    title_key = "gameplay"

    def __init__(self, app):
        s = app.settings

        def rule(key):
            return lambda: s.rules[key]

        def set_rule(key):
            return lambda v: s.set_rule(key, v)

        super().__init__(app, [
            Choice("preset", [("nes", "preset_nes"), ("nes_plus", "preset_nes_plus"), ("modern", "preset_modern")],
                   lambda: s.data["preset"], s.apply_preset, "help_preset", {"custom": "preset_custom"}),
            Choice("rotation", [("nes", "rot_nes"), ("nes_plus", "rot_nes_plus"), ("srs", "rot_srs")],
                   rule("rotation"), set_rule("rotation"), "help_rotation"),
            Choice("randomizer", [("nes", "rand_nes"), ("bag", "rand_bag"), ("random", "rand_random")],
                   rule("randomizer"), set_rule("randomizer"), "help_randomizer"),
            Toggle("hold_piece", rule("hold"), set_rule("hold")),
            Range("next_count", 0, 5, rule("next_count"), set_rule("next_count")),
            Toggle("hard_drop", rule("hard_drop"), set_rule("hard_drop")),
            Toggle("ghost", lambda: s.visual["ghost"], lambda v: s.set_visual("ghost", v)),
            Range("lock_delay", 0, 60, rule("lock_delay"), set_rule("lock_delay"), step=5,
                  fmt=lambda v: t("lock_nes") if v == 0 else _frames(v), help_key="help_lock_delay"),
            Range("das", 1, 30, rule("das"), set_rule("das"), fmt=_frames, help_key="help_das"),
            Range("arr", 0, 15, rule("arr"), set_rule("arr"),
                  fmt=lambda v: t("instant") if v == 0 else _frames(v), help_key="help_arr"),
            Range("soft_drop_speed", 1, 6, rule("soft_drop_frames"), set_rule("soft_drop_frames"), fmt=_frames),
            Range("entry_delay", -1, 20, rule("entry_delay"), set_rule("entry_delay"),
                  fmt=lambda v: t("entry_nes") if v < 0 else _frames(v), help_key="help_entry_delay"),
            Range("line_clear_delay", 0, 30, rule("line_clear_frames"), set_rule("line_clear_frames"), fmt=_frames),
            Range("garbage_density", 1, 9, rule("garbage_density"), set_rule("garbage_density"),
                  help_key="help_density"),
            Item("back", app.pop),
        ])
        self.area = pygame.Rect(W // 2 - 420, 140, 840, 10 * self.row_h)


DEMO_ROWS = [
    "Z.........",
    "ZZ......OO",
    "LZ.T....OO",
    "LJTTT..SSI",
    "LJJJ.ZSS.I",
    "OOTZZJIIII",
]


class AppearanceScene(OptionsSubScene):
    title_key = "appearance"

    def __init__(self, app):
        s = app.settings
        v = s.visual

        def set_theme(key):
            # Cada tema trae su estilo de bloque (luego se puede cambiar). La fuente no se toca.
            s.set_visual("theme", key)
            s.set_visual("block_style", THEMES[key].default_style)

        def setter(key):
            return lambda value: s.set_visual(key, value)

        def set_font(kind):
            s.set_visual("font", kind)
            app.text.kind = kind

        super().__init__(app, [
            Choice("theme", [(k, f"theme_{k}") for k in THEMES], lambda: v["theme"], set_theme),
            Choice("block_style", [(k, f"style_{k}") for k in BLOCK_STYLES], lambda: v["block_style"],
                   setter("block_style")),
            Choice("font", [("pixel", "font_pixel"), ("rounded", "font_rounded"), ("smooth", "font_smooth")],
                   lambda: v["font"], set_font),
            Toggle("grid", lambda: v["grid"], setter("grid")),
            Toggle("ghost", lambda: v["ghost"], setter("ghost")),
            Toggle("show_stats", lambda: v["show_stats"], setter("show_stats")),
            Choice("clear_anim", [(k, f"anim_{k}") for k in CLEAR_ANIMATIONS], lambda: v["clear_anim"],
                   setter("clear_anim")),
            Toggle("quad_flash", lambda: v["quad_flash"], setter("quad_flash")),
            Toggle("callouts", lambda: v["callouts"], setter("callouts")),
            Toggle("crt", lambda: v["crt"], setter("crt"), help_key="help_crt"),
            Item("back", app.pop),
        ])
        self.area = pygame.Rect(90, 140, 720, 10 * self.row_h)
        self.preview = Game(GameRules(rotation="nes", next_count=0, hold=False, line_clear_frames=24), seed=1)
        board = self.preview.board
        for i, row in enumerate(DEMO_ROWS):
            y = board.height - len(DEMO_ROWS) + i
            board.cells[y] = [None if c == "." else c for c in row]
        self.preview.piece = ActivePiece("T", 0, 5, 8)
        self.frame = 0

    def update(self) -> None:
        self.frame += 1
        game = self.preview
        game.level = (self.frame // 150) % 10
        # Cada 3 s se repite la animación de borrar línea sobre la fila inferior.
        cycle = self.frame % 180
        if cycle == 120:
            game.state, game.clearing_rows, game.timer = "clearing", [game.board.height - 1], 24
        elif game.state == "clearing":
            game.timer -= 1
            if game.timer <= 0:
                game.state, game.clearing_rows = "falling", []

    def draw(self, surf) -> None:
        super().draw(surf)
        theme = self.app.theme
        cell = 22
        rect = pygame.Rect(900, 170, 10 * cell, 20 * cell)
        self.app.text.draw(surf, t("preview"), (rect.centerx, 128), theme.text_dim, 2, align="center")
        self.app.renderer.board(surf, self.preview, theme, self.app.settings.visual, rect, cell)


class SoundScene(OptionsSubScene):
    title_key = "sound"

    def __init__(self, app):
        a = app.settings.audio
        pct = lambda v: f"{v}%"  # noqa: E731
        super().__init__(app, [
            Range("sfx_volume", 0, 100, lambda: a["sfx_volume"], lambda v: a.__setitem__("sfx_volume", v),
                  step=10, fmt=pct),
            Range("music_volume", 0, 100, lambda: a["music_volume"], lambda v: a.__setitem__("music_volume", v),
                  step=10, fmt=pct),
            Item("back", app.pop),
        ])
        self.area = pygame.Rect(W // 2 - 380, 200, 760, 3 * self.row_h)

    def enter(self) -> None:
        self.app.audio.play_music()

    def leave(self) -> None:
        super().leave()
        self.app.audio.stop_music()

    def on_change(self, item) -> None:
        self.app.apply_settings()
        if item is self.items[0]:
            self.app.audio.play("clear2")
        elif self.app.settings.audio["music_volume"] > 0:
            self.app.audio.play_music()


# --- controles ----------------------------------------------------------------

class ControlsScene(Scene):
    COLUMNS = ("col_primary", "col_secondary", "col_gamepad")

    def __init__(self, app):
        super().__init__(app)
        self.nav = NavReader()
        self.row = 0
        self.col = 0
        self.capturing = False
        self.cells: list[tuple[int, int, pygame.Rect]] = []
        for action in Action.ALL:
            slots = app.settings.controls.setdefault(action, ["", "", ""])
            slots.extend([""] * (3 - len(slots)))

    @property
    def rows(self) -> int:
        return len(Action.ALL) + 2   # acciones + restaurar + volver

    def leave(self) -> None:
        self.app.settings.save()

    def _assign(self, binding: str) -> None:
        controls = self.app.settings.controls
        for slots in controls.values():
            for i, existing in enumerate(slots):
                if existing == binding:
                    slots[i] = ""
        controls[Action.ALL[self.row]][self.col] = binding
        self.app.audio.play("menu_select")

    def _activate(self) -> None:
        if self.row < len(Action.ALL):
            self.capturing = True
        elif self.row == len(Action.ALL):
            self.app.settings.reset_controls()
            self.app.input.controls = self.app.settings.controls
            self.app.audio.play("menu_select")
        else:
            self.app.pop()

    def handle_event(self, event) -> None:
        if self.capturing:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.capturing = False
                return
            binding = event_to_binding(event, gamepad_only=self.col == 2, keyboard_only=self.col < 2)
            if binding:
                self._assign(binding)
                self.capturing = False
            return
        if event.type == pygame.MOUSEMOTION:
            for row, col, rect in self.cells:
                if rect.collidepoint(event.pos):
                    self.row, self.col = row, max(0, col)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, col, rect in self.cells:
                if rect.collidepoint(event.pos):
                    self.row, self.col = row, max(0, col)
                    self._activate()
            return
        nav = self.nav.read(event)
        if nav == NAV_UP:
            self.row = (self.row - 1) % self.rows
        elif nav == NAV_DOWN:
            self.row = (self.row + 1) % self.rows
        elif nav == NAV_LEFT:
            self.col = (self.col - 1) % 3
        elif nav == NAV_RIGHT:
            self.col = (self.col + 1) % 3
        elif nav == NAV_ACCEPT:
            self._activate()
        elif nav == NAV_DELETE and self.row < len(Action.ALL):
            self.app.settings.controls[Action.ALL[self.row]][self.col] = ""
        elif nav == NAV_BACK:
            self.app.pop()
        if nav is not None:
            self.app.audio.play("menu_move")

    def draw(self, surf) -> None:
        app = self.app
        theme, txt = app.theme, app.text
        app.renderer.background(surf, theme)
        txt.draw(surf, t("controls"), (W // 2, 40), theme.text, 6, align="center",
                 shadow=theme.shadow(0.5))
        panel = pygame.Rect(80, 120, W - 160, 520)
        app.renderer.panel(surf, panel, theme)
        col_x = [600, 825, 1050]
        for i, key in enumerate(self.COLUMNS):
            txt.draw(surf, t(key), (col_x[i], 136), theme.text_dim, 2, align="center")
        self.cells = []
        controls = app.settings.controls
        row_h = 44
        for r, action in enumerate(Action.ALL):
            y = 170 + r * row_h
            txt.draw(surf, t(ACTION_LABELS[action]), (110, y + 8), theme.text, 3)
            for c in range(3):
                rect = pygame.Rect(0, y, 210, row_h - 6)
                rect.centerx = col_x[c]
                self.cells.append((r, c, rect))
                selected = r == self.row and c == self.col
                if selected:
                    color = theme.accent
                    pygame.draw.rect(surf, color, rect, width=2, border_radius=4)
                label = "..." if selected and self.capturing else binding_label(controls[action][c])
                txt.draw(surf, label, (rect.centerx, y + 8), theme.accent if selected else theme.text_dim,
                         2 if len(label) > 10 else 3, align="center")
        for i, key in enumerate(("reset_controls", "back")):
            r = len(Action.ALL) + i
            y = 170 + r * row_h + 10
            rect = pygame.Rect(0, y, 420, row_h - 6)
            rect.centerx = W // 2
            self.cells.append((r, -1, rect))
            if r == self.row:
                pygame.draw.rect(surf, theme.accent, rect, width=2, border_radius=4)
            txt.draw(surf, t(key), (rect.centerx, y + 8), theme.text if r == self.row else theme.text_dim, 3,
                     align="center")
        if self.capturing:
            msg = t("press_button") if self.col == 2 else t("press_key")
            txt.draw(surf, msg, (W // 2, H - 56), theme.accent, 3, align="center")
        else:
            txt.draw(surf, t("controls_help"), (W // 2, H - 52), theme.text_dim, 2, align="center")


# --- récords ------------------------------------------------------------------

class ScoresScene(Scene):
    def __init__(self, app, mode: str = "marathon", highlight: int = -1):
        super().__init__(app)
        self.mode = mode if mode in MODES else "marathon"
        self.highlight = highlight
        self.nav = NavReader()
        self.frame = 0

    def update(self) -> None:
        self.frame += 1

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.app.pop()
            return
        nav = self.nav.read(event)
        if nav in (NAV_LEFT, NAV_RIGHT):
            i = MODES.index(self.mode) + (1 if nav == NAV_RIGHT else -1)
            self.mode = MODES[i % len(MODES)]
            self.highlight = -1
            self.app.audio.play("menu_move")
        elif nav in (NAV_ACCEPT, NAV_BACK):
            self.app.pop()

    def draw(self, surf) -> None:
        app = self.app
        theme, txt = app.theme, app.text
        app.renderer.background(surf, theme)
        txt.draw(surf, t("highscores"), (W // 2, 40), theme.text, 6, align="center",
                 shadow=theme.shadow(0.5))
        txt.draw(surf, f"< {t(MODE_LABELS[self.mode])} >", (W // 2, 120), theme.accent, 3, align="center")
        panel = pygame.Rect(120, 170, W - 240, 460)
        app.renderer.panel(surf, panel, theme)
        table = app.scores.table(self.mode)
        headers = [("#", 170, "left"), (t("name"), 230, "left"), (t("score"), 700, "right"),
                   (t("lines"), 830, "right"), (t("level"), 950, "right"), (t("time"), 1120, "right")]
        for label, x, align in headers:
            txt.draw(surf, label, (x, 186), theme.text_dim, 2, align=align)
        if not table:
            txt.draw(surf, t("no_scores"), (W // 2, 380), theme.text_dim, 3, align="center")
        for i, entry in enumerate(table):
            y = 220 + i * 40
            blink = i == self.highlight and (self.frame // 20) % 2 == 0
            color = theme.accent if i == self.highlight else theme.text
            if blink:
                color = theme.text
            values = [(f"{i + 1}", 170, "left"), (entry.get("name", "")[:12], 230, "left"),
                      (f"{entry['score']}", 700, "right"), (f"{entry['lines']}", 830, "right"),
                      (f"{entry['level']}", 950, "right"),
                      (format_time(entry["frames"], precise=True), 1120, "right")]
            for text, x, align in values:
                txt.draw(surf, text, (x, y), color, 3, align=align)
        txt.draw(surf, t("scores_help"), (W // 2, H - 52), theme.text_dim, 2, align="center")


class NameEntryScene(Scene):
    MAX_LEN = 12

    def __init__(self, app, mode: str, entry: dict):
        super().__init__(app)
        self.mode = mode
        self.entry = entry
        self.name = app.settings.data.get("player_name") or t("player")
        self.fresh = True
        self.frame = 0
        self.nav = NavReader()

    def enter(self) -> None:
        pygame.key.start_text_input()
        self.app.audio.play("won")

    def update(self) -> None:
        self.frame += 1

    def handle_event(self, event) -> None:
        if event.type == pygame.TEXTINPUT:
            if self.fresh:
                self.name, self.fresh = "", False
            self.name = (self.name + event.text)[: self.MAX_LEN]
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            self.fresh = False
            self.name = self.name[:-1]
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            self._confirm()
        elif event.type == pygame.JOYBUTTONDOWN and self.nav.read(event) == NAV_ACCEPT:
            self._confirm()

    def _confirm(self) -> None:
        name = self.name.strip() or t("player")
        self.app.settings.data["player_name"] = name
        self.app.settings.save()
        self.entry["name"] = name
        rank = self.app.scores.add(self.mode, self.entry)
        self.app.replace(ScoresScene(self.app, self.mode, rank))

    def draw(self, surf) -> None:
        app = self.app
        theme, txt = app.theme, app.text
        app.renderer.background(surf, theme)
        txt.draw(surf, t("new_record"), (W // 2, 150), theme.accent, 6, align="center",
                 shadow=theme.shadow(0.5))
        txt.draw(surf, f"{t('score')} {self.entry['score']}", (W // 2, 260), theme.text, 3, align="center")
        txt.draw(surf, t("enter_name"), (W // 2, 340), theme.text_dim, 3, align="center")
        box = pygame.Rect(0, 0, 520, 70)
        box.center = (W // 2, 430)
        app.renderer.panel(surf, box, theme)
        shown = self.name + ("_" if (self.frame // 20) % 2 == 0 else " ")
        txt.draw(surf, shown, (box.centerx, box.y + 14), theme.accent if self.fresh else theme.text, 4,
                 align="center")
