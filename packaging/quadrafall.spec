# -*- mode: python ; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Especificación de PyInstaller, válida en Windows y Linux.
# Uso (desde la raíz del proyecto):  pyinstaller packaging/quadrafall.spec
import sys
from pathlib import Path

root = Path(SPECPATH).parent

a = Analysis(
    [str(root / "packaging" / "launcher.py")],
    pathex=[str(root / "src")],
    datas=[(str(root / "src" / "quadrafall" / "assets"), "quadrafall/assets")],
    excludes=["tkinter", "numpy", "unittest", "pydoc"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Quadrafall",
    console=False,
    icon=str(root / "packaging" / "windows" / "icon.ico") if sys.platform == "win32" else None,
)
coll = COLLECT(exe, a.binaries, a.datas, name="Quadrafall")
