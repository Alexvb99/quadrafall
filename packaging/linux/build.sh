#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Compila Quadrafall para Linux con PyInstaller.
#   Resultado: dist/Quadrafall/Quadrafall  y  dist/Quadrafall-<versión>-linux-x86_64.tar.gz
set -eu
cd "$(dirname "$0")/../.."

PYTHON="${PYTHON:-python3}"
if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; fi

"$PYTHON" -m pip install --quiet -e ".[dev]"
"$PYTHON" -m pytest -q
"$PYTHON" -m PyInstaller --noconfirm --clean packaging/quadrafall.spec

VERSION="$("$PYTHON" -c 'import sys; sys.path.insert(0, "src"); import quadrafall; print(quadrafall.__version__)')"
cp LICENSE README.md dist/Quadrafall/
cp packaging/linux/io.github.quadrafall.Quadrafall.desktop packaging/linux/io.github.quadrafall.Quadrafall.png dist/Quadrafall/
tar -C dist -czf "dist/Quadrafall-$VERSION-linux-$(uname -m).tar.gz" Quadrafall
echo "Listo: dist/Quadrafall-$VERSION-linux-$(uname -m).tar.gz"
