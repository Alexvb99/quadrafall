# SPDX-License-Identifier: GPL-3.0-or-later
"""Ventana, bucle principal y pila de escenas."""

from __future__ import annotations

import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from . import APP_NAME  # noqa: E402
from .audio import Audio  # noqa: E402
from .engine.game import FPS  # noqa: E402
from .i18n import set_language, t  # noqa: E402
from .paths import asset_path  # noqa: E402
from .scores import HighScores  # noqa: E402
from .settings import Settings  # noqa: E402
from .ui.font import Text  # noqa: E402
from .ui.input import InputMapper  # noqa: E402
from .ui.render import H, W, Renderer  # noqa: E402
from .ui.themes import THEMES  # noqa: E402

STEP = 1.0 / FPS
MAX_STEPS_PER_FRAME = 5


class App:
    def __init__(self, screenshot: str | None = None):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.settings = Settings().load()
        set_language(self.settings.data["language"])
        self.screen = self._open_window()
        pygame.display.set_caption(APP_NAME)
        self._set_icon()
        self.text = Text(self.settings.visual["font"])
        self.renderer = Renderer(self.text)
        self.audio = Audio()
        self.input = InputMapper(self.settings.controls)
        self.scores = HighScores().load()
        self.fullscreen = False
        self.stack: list = []
        self.running = True
        self.toast: tuple[str, int] | None = None
        self.screenshot = screenshot
        self.apply_settings()
        if self.settings.visual["fullscreen"]:
            self.set_fullscreen(True)

        from .ui.screens import TitleScene
        self.push(TitleScene(self))

    # --- ventana ---------------------------------------------------------------

    def _open_window(self) -> pygame.Surface:
        flags = pygame.SCALED | pygame.RESIZABLE
        try:
            screen = pygame.display.set_mode((W, H), flags, vsync=1)
            self.vsync = True
        except pygame.error:
            screen = pygame.display.set_mode((W, H), flags)
            self.vsync = False
        return screen

    def _set_icon(self) -> None:
        try:
            pygame.display.set_icon(pygame.image.load(str(asset_path("icon.png"))))
        except (pygame.error, FileNotFoundError):
            pass

    def set_fullscreen(self, value: bool) -> None:
        self.settings.visual["fullscreen"] = value
        if value != self.fullscreen:
            pygame.display.toggle_fullscreen()
            self.fullscreen = value

    @property
    def theme(self):
        return THEMES.get(self.settings.visual["theme"], THEMES["nes"])

    def apply_settings(self) -> None:
        self.text.kind = self.settings.visual["font"]
        audio = self.settings.audio
        self.audio.set_volumes(audio["sfx_volume"] / 100, audio["music_volume"] / 100)
        self.input.controls = self.settings.controls

    def show_toast(self, message: str) -> None:
        self.toast = (message, 180)

    # --- escenas ---------------------------------------------------------------

    @property
    def scene(self):
        return self.stack[-1]

    def _activate(self, scene) -> None:
        pygame.key.set_repeat(260, 45) if scene.key_repeat else pygame.key.set_repeat(0)

    def push(self, scene) -> None:
        self.stack.append(scene)
        self._activate(scene)
        scene.enter()

    def pop(self) -> None:
        scene = self.stack.pop()
        scene.leave()
        if not self.stack:
            self.running = False
            return
        self._activate(self.scene)   # la escena anterior conserva su estado

    def replace(self, scene) -> None:
        old = self.stack.pop()
        old.leave()
        self.push(scene)

    def quit(self) -> None:
        self.running = False

    # --- bucle -----------------------------------------------------------------

    def run(self) -> None:
        clock = pygame.time.Clock()
        accumulator = 0.0
        cap = 0 if self.vsync else FPS
        fast_frames = 0
        frame = 0
        while self.running:
            dt = clock.tick(cap) / 1000.0
            frame += 1
            # Si la sincronía vertical no funciona, limitamos a 60 fps para no gastar CPU.
            if cap == 0 and frame < 120:
                fast_frames += dt < 0.004
                if fast_frames > 30:
                    cap = FPS
            for event in pygame.event.get():
                self._handle_event(event)
                if not self.running:
                    break
            accumulator += min(dt, 0.25)
            steps = 0
            while accumulator >= STEP and steps < MAX_STEPS_PER_FRAME and self.running:
                self.scene.update()
                accumulator -= STEP
                steps += 1
            if steps == MAX_STEPS_PER_FRAME:
                accumulator = 0.0
            if self.toast:
                self.toast = (self.toast[0], self.toast[1] - steps) if self.toast[1] > 0 else None
            if self.running:
                self._draw()
                if self.screenshot and frame == 30:
                    pygame.image.save(self.screen, self.screenshot)
                    self.running = False
        self.settings.save()
        pygame.quit()

    def _handle_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        name = self.input.handle_device_event(event)
        if name:
            self.show_toast(t("gamepad_connected", name=name[:28]))
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_F11 or
                                             (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
            self.set_fullscreen(not self.fullscreen)
            self.settings.save()
            return
        self.scene.handle_event(event)

    def _draw(self) -> None:
        # Se dibuja desde la última escena opaca hacia arriba (p. ej. partida + pausa).
        start = len(self.stack) - 1
        while start > 0 and not self.stack[start].opaque:
            start -= 1
        for scene in self.stack[start:]:
            scene.draw(self.screen)
        if self.settings.visual["crt"]:
            self.renderer.crt(self.screen)
        if self.toast:
            theme = self.theme
            self.text.draw(self.screen, self.toast[0], (W - 20, 16), theme.accent, 2, align="right")
        pygame.display.flip()


def main() -> None:
    screenshot = None
    if "--screenshot" in sys.argv:
        screenshot = sys.argv[sys.argv.index("--screenshot") + 1]
    App(screenshot).run()


if __name__ == "__main__":
    main()
