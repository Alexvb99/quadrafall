#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Compila Quadrafall para Linux.
#   dist/Quadrafall/Quadrafall                       (carpeta del programa)
#   dist/Quadrafall-<versión>-Linux-<arq>.tar.gz     (sin instalar)
#   dist/Quadrafall-<versión>-Linux-<arq>.AppImage   (si hay appimagetool)
#   dist/quadrafall_<versión>_<arq>.deb              (si hay dpkg-deb)
# Variable opcional: APPIMAGETOOL = ruta de appimagetool.
set -eu
cd "$(dirname "$0")/../.."

PYTHON="${PYTHON:-python3}"
if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; fi

"$PYTHON" -m pip install --quiet -e ".[dev]"
"$PYTHON" -m pytest -q
"$PYTHON" -m PyInstaller --noconfirm --clean packaging/quadrafall.spec

VERSION="$("$PYTHON" -c 'import sys; sys.path.insert(0, "src"); import quadrafall; print(quadrafall.__version__)')"
ARCH="$(uname -m)"
cp LICENSE README.md dist/Quadrafall/

tar -C dist -czf "dist/Quadrafall-$VERSION-Linux-$ARCH.tar.gz" Quadrafall
echo "Listo: dist/Quadrafall-$VERSION-Linux-$ARCH.tar.gz"

sh packaging/linux/make_appimage.sh "$VERSION"
sh packaging/linux/make_deb.sh "$VERSION"
