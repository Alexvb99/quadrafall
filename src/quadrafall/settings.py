# SPDX-License-Identifier: GPL-3.0-or-later
"""Ajustes del jugador: reglas, apariencia, sonido y controles (JSON)."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from .engine.game import GameRules
from .paths import config_dir

# Estilos de juego predefinidos. Cambiar cualquier opción afectada pasa a "custom".
PRESETS: dict[str, dict] = {
    "nes": {
        "rules": dict(rotation="nes", randomizer="nes", hold=False, next_count=1, hard_drop=False,
                      lock_delay=0, lock_resets=0, das=16, arr=6, soft_drop_frames=2, entry_delay=-1,
                      line_clear_frames=20),
        "visual": dict(ghost=False),
    },
    "nes_plus": {
        # Como el NES, pero con al menos 1/3 s apoyada para colar la pieza en un hueco.
        "rules": dict(rotation="nes_plus", randomizer="nes", hold=True, next_count=3, hard_drop=True,
                      lock_delay=20, lock_resets=6, das=12, arr=4, soft_drop_frames=2, entry_delay=-1,
                      line_clear_frames=20),
        "visual": dict(ghost=True),
    },
    "modern": {
        "rules": dict(rotation="srs", randomizer="bag", hold=True, next_count=5, hard_drop=True,
                      lock_delay=30, lock_resets=15, das=10, arr=2, soft_drop_frames=1,
                      entry_delay=6, line_clear_frames=12),
        "visual": dict(ghost=True),
    },
}

# Asignaciones: "key:<nombre pygame>", "btn:<n>", "hat:<x>,<y>", "axis:<n>:<+|->".
# Por acción: [principal, secundaria, mando]. "" = sin asignar.
DEFAULT_CONTROLS: dict[str, list[str]] = {
    "left": ["key:left", "key:a", "hat:-1,0"],
    "right": ["key:right", "key:d", "hat:1,0"],
    "soft_drop": ["key:down", "key:s", "hat:0,-1"],
    "hard_drop": ["key:space", "key:w", "hat:0,1"],
    "rotate_cw": ["key:x", "key:up", "btn:1"],
    "rotate_ccw": ["key:z", "key:left ctrl", "btn:0"],
    "hold": ["key:c", "key:left shift", "btn:2"],
    "pause": ["key:escape", "key:p", "btn:7"],
}

DEFAULTS: dict = {
    "language": "auto",
    "player_name": "",
    "preset": "nes_plus",
    "rules": GameRules().to_dict(),
    "visual": {
        "theme": "nes",
        "block_style": "nes",
        "font": "pixel",
        "ghost": True,
        "grid": True,
        "show_stats": True,
        "clear_anim": "nes",
        "quad_flash": True,
        "callouts": True,
        "crt": False,
        "fullscreen": False,
    },
    "audio": {"sfx_volume": 70, "music_volume": 50},
    "controls": DEFAULT_CONTROLS,
}


def _merge(defaults: dict, data: dict) -> dict:
    result = copy.deepcopy(defaults)
    for key, value in data.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge(result[key], value)
        elif key in result and (result[key] is None or type(value) is type(result[key])
                                or isinstance(value, (int, float)) and isinstance(result[key], (int, float))):
            result[key] = value
    return result


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = path or config_dir() / "settings.json"
        self.data = copy.deepcopy(DEFAULTS)

    def load(self) -> Settings:
        try:
            with open(self.path, encoding="utf-8") as fh:
                self.data = _merge(DEFAULTS, json.load(fh))
        except (OSError, ValueError):
            self.data = copy.deepcopy(DEFAULTS)
        # Un estilo predefinido siempre usa sus valores actuales (si se retocan en una
        # nueva versión, los jugadores que lo tengan elegido reciben el cambio).
        if self.data["preset"] in PRESETS:
            self.apply_preset(self.data["preset"])
        return self

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except OSError:
            pass  # sin permisos de escritura: se juega igual, sin guardar

    # --- accesos cómodos --------------------------------------------------------

    @property
    def rules(self) -> dict:
        return self.data["rules"]

    @property
    def visual(self) -> dict:
        return self.data["visual"]

    @property
    def audio(self) -> dict:
        return self.data["audio"]

    @property
    def controls(self) -> dict[str, list[str]]:
        return self.data["controls"]

    def game_rules(self) -> GameRules:
        return GameRules.from_dict(self.rules)

    def apply_preset(self, name: str) -> None:
        self.data["preset"] = name
        preset = PRESETS.get(name)
        if preset:
            self.rules.update(preset["rules"])
            self.visual.update(preset["visual"])

    def set_rule(self, key: str, value) -> None:
        self.rules[key] = value
        self._refresh_preset()

    def set_visual(self, key: str, value) -> None:
        self.visual[key] = value
        if key == "ghost":
            self._refresh_preset()

    def _refresh_preset(self) -> None:
        """Si la combinación actual coincide con un estilo predefinido, lo marca."""
        for name, preset in PRESETS.items():
            if all(self.rules.get(k) == v for k, v in preset["rules"].items()) and \
               all(self.visual.get(k) == v for k, v in preset["visual"].items()):
                self.data["preset"] = name
                return
        self.data["preset"] = "custom"

    def reset_controls(self) -> None:
        self.data["controls"] = copy.deepcopy(DEFAULT_CONTROLS)
