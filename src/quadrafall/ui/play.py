# SPDX-License-Identifier: GPL-3.0-or-later
"""Escena de partida, menú de pausa y final de partida."""

from __future__ import annotations

import pygame

from ..engine.game import Action, Game
from ..i18n import t
from ..scores import HighScores
from .input import event_to_binding
from .menu import NAV_ACCEPT, NAV_BACK, Item, MenuScene, NavReader, Scene
from .render import H, W, Layout, format_time
from .themes import darken

MODE_LABELS = {"marathon": "mode_marathon", "btype": "mode_btype", "sprint": "mode_sprint"}
CALLOUTS = {"clear1": "single", "clear2": "double", "clear3": "triple", "clear4": "quad"}
CURTAIN_FRAMES = 45


class GameScene(Scene):
    key_repeat = False

    def __init__(self, app):
        super().__init__(app)
        self.nav = NavReader()
        self.start()

    def start(self) -> None:
        settings = self.app.settings
        self.rules = settings.game_rules()
        self.game = Game(self.rules)
        self.layout = Layout(self.rules, settings.visual)
        self.popups: list[list] = []        # [texto, fotogramas restantes, color]
        self.end_frames = 0
        self.paused = False
        self.qualifies = False
        self.entry: dict | None = None
        best = self.app.scores.best(self.rules.mode)
        self.best = best["score"] if best else 0
        self.app.input.reset()
        self.app.audio.stop_music()
        self.app.audio.play_music()

    # --- eventos ---------------------------------------------------------------

    def handle_event(self, event) -> None:
        if event.type == pygame.WINDOWFOCUSLOST and not self.game.finished:
            self.pause()
            return
        if self.game.finished:
            if self.end_frames > CURTAIN_FRAMES + 15 and self.nav.read(event) in (NAV_ACCEPT, NAV_BACK):
                self.finish()
            return
        self.app.input.note_event(event)

    def update(self) -> None:
        held, pressed = self.app.input.poll()
        game = self.game
        if not game.finished:
            if Action.PAUSE in pressed:
                self.pause()
                return
            game.update(held, pressed)
            self._react(game.events)
            if game.finished:
                self._on_finished()
        else:
            self.end_frames += 1
        for popup in self.popups:
            popup[1] -= 1
        self.popups = [p for p in self.popups if p[1] > 0]

    def _react(self, events: list[str]) -> None:
        audio = self.app.audio
        theme = self.app.theme
        for event in events:
            if event == "lock" and "hard_drop" in events:
                continue
            audio.play(event)
            if not self.app.settings.visual["callouts"]:
                continue
            if event in CALLOUTS:
                color = theme.accent if event == "clear4" else theme.text
                self.popups.append([t(CALLOUTS[event]), 70, color])
            elif event == "level_up":
                self.popups.append([t("level_up", n=self.game.level), 90, theme.accent])

    def _on_finished(self) -> None:
        self.app.audio.stop_music()
        game = self.game
        self.entry = HighScores.make_entry(game)
        self.qualifies = self.app.scores.qualifies(self.rules.mode, self.entry, game.state == "won")

    def finish(self) -> None:
        if self.qualifies:
            from .screens import NameEntryScene
            self.app.replace(NameEntryScene(self.app, self.rules.mode, self.entry))
        else:
            self.app.pop()

    def pause(self) -> None:
        self.paused = True
        self.app.audio.pause_music(True)
        self.app.audio.play("pause")
        self.app.push(PauseScene(self.app, self))

    def resume(self) -> None:
        self.paused = False
        self.app.audio.pause_music(False)
        self.app.input.reset()

    # --- dibujo ----------------------------------------------------------------

    def draw(self, surf) -> None:
        app = self.app
        renderer, theme, visual, txt = app.renderer, app.theme, app.settings.visual, app.text
        game, layout = self.game, self.layout
        renderer.background(surf, theme)
        curtain = 0
        if game.state == "over":
            curtain = int(min(1.0, self.end_frames / CURTAIN_FRAMES) * game.board.visible_height)
        renderer.board(surf, game, theme, visual, layout.board, hide_pieces=self.paused, curtain_rows=curtain)
        renderer.hud(surf, game, layout, theme, visual, self.best, t(MODE_LABELS[self.rules.mode]))

        for text, frames, color in ([] if self.paused else self.popups):
            rise = (90 - frames) // 3
            txt.draw(surf, text, (layout.board.centerx, layout.board.y + 200 - rise), color, 4,
                     align="center", shadow=darken(theme.board, 0.5) if theme.ornaments else None)

        if game.finished and self.end_frames > CURTAIN_FRAMES:
            self._draw_results(surf)

    def _draw_results(self, surf) -> None:
        app = self.app
        theme, txt, game = app.theme, app.text, self.game
        board = self.layout.board
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((*theme.background2, 150))
        surf.blit(veil, (0, 0))
        box = pygame.Rect(0, 0, 480, 330)
        box.center = (board.centerx, board.centery)
        app.renderer.panel(surf, box, theme)
        title = t("you_win") if game.state == "won" else t("game_over")
        txt.draw(surf, title, (box.centerx, box.y + 20), theme.accent, 4, align="center")
        rows = [
            (t("score"), f"{game.score}"),
            (t("lines"), f"{game.lines}"),
            (t("level"), f"{game.level}"),
            (t("time"), format_time(game.frames, precise=True)),
        ]
        for i, (label, value) in enumerate(rows):
            y = box.y + 80 + i * 40
            txt.draw(surf, label, (box.x + 40, y + 6), theme.text_dim, 2)
            txt.draw(surf, value, (box.right - 40, y), theme.text, 3, align="right")
        if self.qualifies:
            txt.draw(surf, t("new_record"), (box.centerx, box.bottom - 80), theme.accent, 3, align="center")
        if (self.end_frames // 30) % 2 == 0:
            txt.draw(surf, t("press_enter"), (box.centerx, box.bottom - 40), theme.text, 2, align="center")


class PauseScene(MenuScene):
    opaque = False

    def __init__(self, app, game_scene: GameScene):
        super().__init__(app, [
            Item("resume", self.on_back),
            Item("restart", self._restart),
            Item("quit_to_menu", self._quit),
        ])
        self.game_scene = game_scene
        self.area = pygame.Rect(W // 2 - 200, 320, 400, 3 * self.row_h)

    def handle_event(self, event) -> None:
        # La tecla/botón de pausa también reanuda (ESC ya lo hace como "volver").
        binding = event_to_binding(event)
        if binding and binding != "key:escape" and binding in self.app.settings.controls.get(Action.PAUSE, []):
            self.on_back()
            return
        super().handle_event(event)

    def on_back(self) -> None:
        self.app.pop()
        self.game_scene.resume()

    def _restart(self) -> None:
        self.app.pop()
        self.game_scene.start()

    def _quit(self) -> None:
        self.app.audio.stop_music()
        self.app.pop()
        self.app.pop()

    def draw_background(self, surf) -> None:
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((*self.app.theme.background2, 170))
        surf.blit(veil, (0, 0))

    def draw(self, surf) -> None:
        self.draw_background(surf)
        theme = self.app.theme
        self.app.text.draw(surf, t("paused"), (W // 2, 230), theme.text, 7, align="center",
                           shadow=theme.shadow(0.6))
        self.draw_items(surf)
