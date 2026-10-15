# SPDX-License-Identifier: GPL-3.0-or-later
"""Escenas y menús genéricos, manejables con teclado, mando o ratón."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pygame

from ..i18n import has, t
from .render import H, W
from .themes import darken, mix


class Scene:
    opaque = True          # False = se dibuja encima de la escena anterior
    key_repeat = True      # repetición de teclas mantenidas (menús sí, partida no)

    def __init__(self, app):
        self.app = app

    def enter(self) -> None: ...
    def leave(self) -> None: ...
    def handle_event(self, event) -> None: ...
    def update(self) -> None: ...
    def draw(self, surf) -> None: ...


# --- navegación común ------------------------------------------------------------

NAV_UP, NAV_DOWN, NAV_LEFT, NAV_RIGHT, NAV_ACCEPT, NAV_BACK, NAV_DELETE = range(7)


class NavReader:
    """Convierte eventos de teclado y mando en órdenes de navegación de menú."""

    def __init__(self):
        self._axis = {0: 0, 1: 0}

    def read(self, event) -> int | None:
        if event.type == pygame.KEYDOWN:
            return {
                pygame.K_UP: NAV_UP, pygame.K_w: NAV_UP,
                pygame.K_DOWN: NAV_DOWN, pygame.K_s: NAV_DOWN,
                pygame.K_LEFT: NAV_LEFT, pygame.K_a: NAV_LEFT,
                pygame.K_RIGHT: NAV_RIGHT, pygame.K_d: NAV_RIGHT,
                pygame.K_RETURN: NAV_ACCEPT, pygame.K_KP_ENTER: NAV_ACCEPT, pygame.K_SPACE: NAV_ACCEPT,
                pygame.K_ESCAPE: NAV_BACK, pygame.K_BACKSPACE: NAV_BACK,
                pygame.K_DELETE: NAV_DELETE,
            }.get(event.key)
        if event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if y == 1:
                return NAV_UP
            if y == -1:
                return NAV_DOWN
            if x == -1:
                return NAV_LEFT
            if x == 1:
                return NAV_RIGHT
        if event.type == pygame.JOYBUTTONDOWN:
            return {0: NAV_ACCEPT, 7: NAV_ACCEPT, 1: NAV_BACK, 6: NAV_BACK, 2: NAV_DELETE}.get(event.button)
        if event.type == pygame.JOYAXISMOTION and event.axis in self._axis:
            direction = 0 if abs(event.value) < 0.5 else (1 if event.value > 0 else -1)
            previous, self._axis[event.axis] = self._axis[event.axis], direction
            if direction and direction != previous:
                if event.axis == 0:
                    return NAV_RIGHT if direction > 0 else NAV_LEFT
                return NAV_DOWN if direction > 0 else NAV_UP
        return None


# --- elementos de menú ---------------------------------------------------------

def _tr(label) -> str:
    if callable(label):
        return label()
    return t(label) if has(label) else str(label)


class Item:
    def __init__(self, label, action: Callable[[], None] | None = None, help_key: str | None = None):
        self._label = label
        self.action = action
        self.help_key = help_key

    @property
    def label(self) -> str:
        return _tr(self._label)

    def value_text(self) -> str | None:
        return None

    def change(self, delta: int) -> bool:
        return False

    def activate(self) -> bool:
        if self.action:
            self.action()
            return True
        return False


class Choice(Item):
    def __init__(self, label, options: Sequence[tuple[object, str]], get: Callable[[], object],
                 set: Callable[[object], None], help_key: str | None = None,
                 extra_labels: dict | None = None):
        super().__init__(label, help_key=help_key)
        self.options = list(options)
        self.get, self.set = get, set
        self.extra_labels = extra_labels or {}

    def _index(self) -> int:
        current = self.get()
        for i, (value, _) in enumerate(self.options):
            if value == current:
                return i
        return -1

    def value_text(self) -> str:
        i = self._index()
        if i < 0:
            return _tr(self.extra_labels.get(self.get(), str(self.get())))
        return _tr(self.options[i][1])

    def change(self, delta: int) -> bool:
        i = self._index()
        i = 0 if i < 0 else (i + delta) % len(self.options)
        self.set(self.options[i][0])
        return True

    def activate(self) -> bool:
        return self.change(1)


class Toggle(Choice):
    def __init__(self, label, get, set, help_key=None):
        super().__init__(label, [(True, "on"), (False, "off")], get, set, help_key)


class Range(Item):
    def __init__(self, label, lo: int, hi: int, get, set, step: int = 1,
                 fmt: Callable[[int], str] | None = None, help_key: str | None = None):
        super().__init__(label, help_key=help_key)
        self.lo, self.hi, self.step = lo, hi, step
        self.get, self.set = get, set
        self.fmt = fmt or str

    def value_text(self) -> str:
        return self.fmt(self.get())

    def change(self, delta: int) -> bool:
        value = max(self.lo, min(self.hi, self.get() + delta * self.step))
        if value == self.get():
            return False
        self.set(value)
        return True


# --- escena de menú ------------------------------------------------------------

class MenuScene(Scene):
    title_key: str | None = None
    row_h = 46

    def __init__(self, app, items: list[Item] | None = None, title_key: str | None = None):
        super().__init__(app)
        self.items = items or []
        if title_key:
            self.title_key = title_key
        self.selected = 0
        self.scroll = 0
        self.nav = NavReader()
        self.area = pygame.Rect(240, 150, 800, 470)   # zona de la lista
        self._rects: list[tuple[int, pygame.Rect]] = []

    # comportamiento ---------------------------------------------------------

    def on_back(self) -> None:
        self.app.pop()

    def on_change(self, item: Item) -> None:
        """Se llama tras modificar un valor (para guardar o aplicar cambios)."""

    def _move(self, delta: int) -> None:
        if self.items:
            self.selected = (self.selected + delta) % len(self.items)
            self.app.audio.play("menu_move")

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEMOTION:
            for index, rect in self._rects:
                if rect.collidepoint(event.pos) and index != self.selected:
                    self.selected = index
            return
        if event.type == pygame.MOUSEWHEEL:
            self._move(-event.y)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            for index, rect in self._rects:
                if rect.collidepoint(event.pos):
                    self.selected = index
                    item = self.items[index]
                    # Clic izquierdo: siguiente valor / activar. Clic derecho: valor anterior.
                    if event.button == 3:
                        self._change(item, -1)
                    elif item.value_text() is not None:
                        self._change(item, 1)
                    else:
                        self._activate(item)
            return
        nav = self.nav.read(event)
        if nav is None or not self.items:
            if nav == NAV_BACK:
                self.on_back()
            return
        item = self.items[self.selected]
        if nav == NAV_UP:
            self._move(-1)
        elif nav == NAV_DOWN:
            self._move(1)
        elif nav in (NAV_LEFT, NAV_RIGHT):
            self._change(item, -1 if nav == NAV_LEFT else 1)
        elif nav == NAV_ACCEPT:
            self._activate(item)
        elif nav == NAV_BACK:
            self.app.audio.play("menu_move")
            self.on_back()

    def _change(self, item: Item, delta: int) -> None:
        if item.change(delta):
            self.app.audio.play("menu_move")
            self.on_change(item)

    def _activate(self, item: Item) -> None:
        is_value = item.value_text() is not None
        if item.activate():
            self.app.audio.play("menu_move" if is_value else "menu_select")
            if is_value:
                self.on_change(item)

    # dibujo -----------------------------------------------------------------

    def draw_background(self, surf) -> None:
        self.app.renderer.background(surf, self.app.theme)

    def draw(self, surf) -> None:
        theme = self.app.theme
        txt = self.app.text
        self.draw_background(surf)
        if self.title_key:
            txt.draw(surf, t(self.title_key), (W // 2, 50), theme.text, 6, align="center", shadow=darken(theme.background2, 0.5))
        self.draw_items(surf)
        self.draw_help(surf)

    def draw_items(self, surf) -> None:
        theme = self.app.theme
        txt = self.app.text
        area = self.area
        visible = max(1, area.h // self.row_h)
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + visible:
            self.scroll = self.selected - visible + 1
        self._rects = []
        panel = area.inflate(40, 24)
        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((*theme.panel, 215))
        surf.blit(overlay, panel)
        pygame.draw.rect(surf, theme.frame, panel, width=3, border_radius=6)
        for row, index in enumerate(range(self.scroll, min(len(self.items), self.scroll + visible))):
            item = self.items[index]
            rect = pygame.Rect(area.x, area.y + row * self.row_h, area.w, self.row_h - 6)
            self._rects.append((index, rect))
            selected = index == self.selected
            if selected:
                pygame.draw.rect(surf, mix(theme.panel, theme.accent, 0.25), rect, border_radius=4)
                pygame.draw.rect(surf, theme.accent, rect, width=2, border_radius=4)
            color = theme.text if selected else theme.text_dim
            value = item.value_text()
            ty = rect.y + (rect.h - 30) // 2
            if value is None:
                txt.draw(surf, item.label, (rect.centerx, ty), color, 3, align="center")
            else:
                txt.draw(surf, item.label, (rect.x + 16, ty), color, 3)
                shown = f"< {value} >" if selected else value
                txt.draw(surf, shown, (rect.right - 16, ty), theme.accent if selected else color, 3, align="right")
        if self.scroll > 0:
            txt.draw(surf, "↑", (area.right + 8, area.y), theme.text_dim, 3)
        if self.scroll + visible < len(self.items):
            txt.draw(surf, "↓", (area.right + 8, area.bottom - 30), theme.text_dim, 3)

    def draw_help(self, surf) -> None:
        theme = self.app.theme
        txt = self.app.text
        item = self.items[self.selected] if self.items else None
        if item and item.help_key:
            draw_wrapped(txt, surf, t(item.help_key), pygame.Rect(140, 640, W - 280, 40), theme.text, 2)
        else:
            txt.draw(surf, t("menu_help"), (W // 2, H - 52), theme.text_dim, 2, align="center")


def draw_wrapped(txt, surf, text: str, rect: pygame.Rect, color, scale: int) -> None:
    """Escribe texto centrado partiendo líneas para que quepa en `rect`."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        attempt = f"{current} {word}".strip()
        if txt.size(attempt, scale)[0] > rect.w and current:
            lines.append(current)
            current = word
        else:
            current = attempt
    if current:
        lines.append(current)
    line_h = txt.font.line_height(scale)
    y = rect.y - (len(lines) - 1) * line_h // 2
    for line in lines:
        txt.draw(surf, line, (rect.centerx, y), color, scale, align="center")
        y += line_h
