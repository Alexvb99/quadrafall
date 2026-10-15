#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Empaqueta dist/Quadrafall como AppImage: un único archivo que funciona en casi
# cualquier distribución sin instalar nada. Uso: make_appimage.sh <versión>
set -eu
cd "$(dirname "$0")/../.."

VERSION="$1"
APP_ID=io.github.alexvb99.Quadrafall
ARCH="$(uname -m)"
TOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [ -z "$TOOL" ]; then
    echo "appimagetool no encontrado: se omite la AppImage (https://github.com/AppImage/appimagetool)"
    exit 0
fi

APPDIR=build/AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/lib" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps" "$APPDIR/usr/share/metainfo"
cp -r dist/Quadrafall "$APPDIR/usr/lib/quadrafall"
cp "packaging/linux/$APP_ID.desktop" "$APPDIR/$APP_ID.desktop"
cp "packaging/linux/$APP_ID.desktop" "$APPDIR/usr/share/applications/"
cp "packaging/linux/$APP_ID.png" "$APPDIR/$APP_ID.png"
cp "packaging/linux/$APP_ID.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/"
ln -sf "$APP_ID.png" "$APPDIR/.DirIcon"
cp "packaging/linux/$APP_ID.metainfo.xml" "$APPDIR/usr/share/metainfo/$APP_ID.appdata.xml"

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/lib/quadrafall/Quadrafall" "$@"
EOF
chmod +x "$APPDIR/AppRun"

OUT="dist/Quadrafall-$VERSION-Linux-$ARCH.AppImage"
ARCH="$ARCH" "$TOOL" "$APPDIR" "$OUT"
chmod +x "$OUT"
echo "Listo: $OUT"
