# SPDX-License-Identifier: GPL-3.0-or-later
"""Ventana, bucle principal y pila de escenas."""

from __future__ import annotations

import os
import sys
import warnings

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
        """Abre una ventana normal y devuelve el lienzo fijo de W×H donde dibujan las escenas.

        No se usa pygame.SCALED: en gestores de ventanas en mosaico (Niri, Sway...) la ventana
        no aceptaba el tamaño que le daba el gestor. El lienzo se escala a la ventana en _present.
        """
        self.windowed_size = self._initial_window_size()
        self._set_windowed()
        self.viewport = pygame.Rect(0, 0, W, H)
        return pygame.Surface((W, H)).convert()

    @staticmethod
    def _initial_window_size() -> tuple[int, int]:
        # Tres cuartos del escritorio, con la proporción del juego.
        try:
            dw, dh = pygame.display.get_desktop_sizes()[0]
        except (pygame.error, IndexError):
            return W, H
        scale = min(dw * 0.75 / W, dh * 0.75 / H)
        return max(320, round(W * scale)), max(180, round(H * scale))

    def _set_icon(self) -> None:
        try:
            pygame.display.set_icon(pygame.image.load(str(asset_path("icon.png"))))
        except (pygame.error, FileNotFoundError):
            pass

    def set_fullscreen(self, value: bool) -> None:
        self.settings.visual["fullscreen"] = value
        if value == self.fullscreen:
            return
        if value:
            self.windowed_size = pygame.display.get_window_size()
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self._set_windowed()
        self.fullscreen = value

    def _set_windowed(self) -> None:
        # Los gestores en mosaico imponen su tamaño: no es un error, el lienzo se adapta.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Requested window was forcibly resized")
            pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

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
        frame = 0
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            frame += 1
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
            self.audio.update()
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
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            event = pygame.event.Event(event.type, {**event.dict, "pos": self._to_canvas(event.pos)})
        name =self.input.handle_device_event(event)
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
        self._present()

    def _present(self) -> None:
        """Escala el lienzo a la ventana, centrado y con bandas si la proporción no coincide."""
        window = pygame.display.get_surface()
        ww, wh = window.get_size()
        scale = min(ww / W, wh / H)
        size = (max(1, round(W * scale)), max(1, round(H * scale)))
        view = pygame.Rect((0, 0), size)
        view.center = (ww // 2, wh // 2)
        self.viewport = view
        bars = self.theme.background2
        window.fill(bars, (0, 0, ww, view.top))
        window.fill(bars, (0, view.bottom, ww, wh - view.bottom))
        window.fill(bars, (0, view.top, view.left, view.height))
        window.fill(bars, (view.right, view.top, ww - view.right, view.height))
        if size == (W, H):
            window.blit(self.screen, view)
        elif scale == int(scale):
            # Escala entera: píxeles nítidos y más rápido.
            pygame.transform.scale(self.screen, size, window.subsurface(view))
        else:
            pygame.transform.smoothscale(self.screen, size, window.subsurface(view))
        pygame.display.flip()

    def _to_canvas(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Pasa una posición del ratón en la ventana a coordenadas del lienzo."""
        view = self.viewport
        return ((pos[0] - view.x) * W // max(1, view.width),
                (pos[1] - view.y) * H // max(1, view.height))


def main() -> None:
    screenshot = None
    if "--screenshot" in sys.argv:
        screenshot = sys.argv[sys.argv.index("--screenshot") + 1]
    App(screenshot).run()


if __name__ == "__main__":
    main()
