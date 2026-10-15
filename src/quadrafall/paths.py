# SPDX-License-Identifier: GPL-3.0-or-later
"""Dónde se guardan ajustes y récords en cada sistema.

- Windows: %APPDATA%\\Quadrafall
- Linux:   $XDG_CONFIG_HOME/quadrafall (ajustes) y $XDG_DATA_HOME/quadrafall (récords)
- Modo portátil: si existe un archivo `portable.txt` junto al ejecutable
  (o en la raíz del proyecto), todo se guarda en la carpeta `data` de al lado.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from . import APP_NAME


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _portable_dir() -> Path | None:
    root = _app_root()
    return root / "data" if (root / "portable.txt").exists() else None


def config_dir() -> Path:
    portable = _portable_dir()
    if portable:
        return portable
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / APP_NAME.lower()


def data_dir() -> Path:
    portable = _portable_dir()
    if portable:
        return portable
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / APP_NAME.lower()


def asset_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "assets" / name
