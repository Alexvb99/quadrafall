# SPDX-License-Identifier: GPL-3.0-or-later
"""Traduce teclado y mandos a acciones del juego según las asignaciones del jugador."""

from __future__ import annotations

import pygame

from ..engine.game import Action
from ..i18n import has, t

AXIS_THRESHOLD = 0.55


class InputMapper:
    def __init__(self, controls: dict[str, list[str]]):
        self.controls = controls
        self.joysticks: dict[int, pygame.joystick.JoystickType] = {}
        self._prev_held: frozenset[str] = frozenset()
        self._pressed_events: set[str] = set()

    # --- dispositivos -----------------------------------------------------------

    def handle_device_event(self, event) -> str | None:
        """Gestiona conexión/desconexión de mandos. Devuelve el nombre si se conectó uno."""
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            self.joysticks[joy.get_instance_id()] = joy
            return joy.get_name()
        if event.type == pygame.JOYDEVICEREMOVED:
            self.joysticks.pop(event.instance_id, None)
        return None

    # --- consultas --------------------------------------------------------------

    def _hat(self) -> tuple[int, int]:
        """Cruceta combinada de todos los mandos (la palanca izquierda cuenta como cruceta)."""
        hx = hy = 0
        for joy in self.joysticks.values():
            if joy.get_numhats():
                x, y = joy.get_hat(0)
                hx, hy = hx or x, hy or y
            if joy.get_numaxes() >= 2:
                ax, ay = joy.get_axis(0), joy.get_axis(1)
                if abs(ax) > AXIS_THRESHOLD:
                    hx = hx or (1 if ax > 0 else -1)
                if abs(ay) > AXIS_THRESHOLD:
                    hy = hy or (-1 if ay > 0 else 1)  # en los ejes, y positiva es abajo
        return hx, hy

    def binding_active(self, binding: str, keys, hat) -> bool:
        kind, _, arg = binding.partition(":")
        if kind == "key":
            try:
                return bool(keys[pygame.key.key_code(arg)])
            except (ValueError, IndexError):
                return False
        if kind == "btn":
            button = int(arg)
            return any(button < j.get_numbuttons() and j.get_button(button) for j in self.joysticks.values())
        if kind == "hat":
            x, y = (int(v) for v in arg.split(","))
            return (x == 0 or hat[0] == x) and (y == 0 or hat[1] == y) and (x or y)
        if kind == "axis":
            axis, sign = arg.split(":")
            axis = int(axis)
            for j in self.joysticks.values():
                if axis < j.get_numaxes():
                    value = j.get_axis(axis)
                    if (value > AXIS_THRESHOLD and sign == "+") or (value < -AXIS_THRESHOLD and sign == "-"):
                        return True
        return False

    def held_actions(self) -> frozenset[str]:
        keys = pygame.key.get_pressed()
        hat = self._hat()
        held = set()
        for action, bindings in self.controls.items():
            if any(b and self.binding_active(b, keys, hat) for b in bindings):
                held.add(action)
        return frozenset(held)

    def note_event(self, event) -> None:
        """Registra pulsaciones para no perder toques muy breves entre fotogramas."""
        binding = event_to_binding(event)
        if binding:
            for action, bindings in self.controls.items():
                if binding in bindings:
                    self._pressed_events.add(action)

    def poll(self) -> tuple[frozenset[str], frozenset[str]]:
        """Devuelve (mantenidas, recién pulsadas) para el siguiente fotograma lógico."""
        held = self.held_actions()
        pressed = (held - self._prev_held) | self._pressed_events
        self._prev_held = held
        self._pressed_events = set()
        return held, frozenset(pressed)

    def reset(self) -> None:
        """Olvida el estado anterior (p. ej. al volver de un menú) para no arrastrar pulsaciones."""
        self._prev_held = self.held_actions()
        self._pressed_events = set()


def event_to_binding(event, gamepad_only: bool = False, keyboard_only: bool = False) -> str | None:
    """Convierte un evento de pygame en una cadena de asignación, si procede."""
    if event.type == pygame.KEYDOWN and not gamepad_only:
        return "key:" + pygame.key.name(event.key)
    if keyboard_only:
        return None
    if event.type == pygame.JOYBUTTONDOWN:
        return f"btn:{event.button}"
    if event.type == pygame.JOYHATMOTION and event.value != (0, 0):
        x, y = event.value
        # Solo direcciones puras para que las diagonales no asignen dos cosas a la vez.
        if x and y:
            return None
        return f"hat:{x},{y}"
    if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.75 and event.axis > 1:
        # Los ejes 0 y 1 (palanca izquierda) ya funcionan como cruceta.
        return f"axis:{event.axis}:{'+' if event.value > 0 else '-'}"
    return None


_ARROWS = {"left": "←", "right": "→", "up": "↑", "down": "↓"}
_HAT_NAMES = {(-1, 0): "←", (1, 0): "→", (0, 1): "↑", (0, -1): "↓"}


def binding_label(binding: str) -> str:
    if not binding:
        return "-"
    kind, _, arg = binding.partition(":")
    if kind == "key":
        if arg in _ARROWS:
            return _ARROWS[arg]
        return t("key_" + arg) if has("key_" + arg) else arg.upper()
    if kind == "btn":
        return t("button", n=int(arg) + 1)
    if kind == "hat":
        x, y = (int(v) for v in arg.split(","))
        return t("dpad", d=_HAT_NAMES.get((x, y), "?"))
    if kind == "axis":
        axis, sign = arg.split(":")
        return t("axis", n=axis, d=sign)
    return binding


ACTION_LABELS = {
    Action.LEFT: "act_left",
    Action.RIGHT: "act_right",
    Action.SOFT_DROP: "act_soft_drop",
    Action.HARD_DROP: "act_hard_drop",
    Action.ROTATE_CW: "act_rotate_cw",
    Action.ROTATE_CCW: "act_rotate_ccw",
    Action.HOLD: "act_hold",
    Action.PAUSE: "act_pause",
}
