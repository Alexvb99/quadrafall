#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Empaqueta dist/Quadrafall como .deb para Ubuntu, Debian y derivadas.
# Instala en /opt/quadrafall, con el comando "quadrafall" y entrada en el menú.
# Uso: make_deb.sh <versión>
set -eu
cd "$(dirname "$0")/../.."

VERSION="$1"
APP_ID=io.github.alexvb99.Quadrafall
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb no encontrado: se omite el paquete .deb"
    exit 0
fi
DEB_ARCH="$(dpkg --print-architecture)"

PKG=build/deb/quadrafall
rm -rf build/deb
mkdir -p "$PKG/DEBIAN" "$PKG/opt" "$PKG/usr/bin" "$PKG/usr/share/applications" \
         "$PKG/usr/share/icons/hicolor/256x256/apps" "$PKG/usr/share/metainfo" "$PKG/usr/share/doc/quadrafall"
cp -r dist/Quadrafall "$PKG/opt/quadrafall"
ln -s /opt/quadrafall/Quadrafall "$PKG/usr/bin/quadrafall"
cp "packaging/linux/$APP_ID.desktop" "$PKG/usr/share/applications/"
cp "packaging/linux/$APP_ID.png" "$PKG/usr/share/icons/hicolor/256x256/apps/"
cp "packaging/linux/$APP_ID.metainfo.xml" "$PKG/usr/share/metainfo/"
cp LICENSE "$PKG/usr/share/doc/quadrafall/copyright"
chmod -R u=rwX,go=rX "$PKG"
chmod 755 "$PKG/opt/quadrafall/Quadrafall"

cat > "$PKG/DEBIAN/control" <<EOF
Package: quadrafall
Version: $VERSION
Section: games
Priority: optional
Architecture: $DEB_ARCH
Installed-Size: $(du -sk "$PKG" | cut -f1)
Maintainer: Alexandru Voivod <alexandruvoivod@gmail.com>
Homepage: https://github.com/Alexvb99/quadrafall
Description: Falling-blocks puzzle with NES-style rules
 Free falling-blocks puzzle inspired by GNOME Quadrapassel and the NES
 classic, with optional modern touches: hold, next queue, hard drop and
 ghost piece. Spanish and English.
EOF

OUT="dist/quadrafall_${VERSION}_${DEB_ARCH}.deb"
dpkg-deb --build --root-owner-group "$PKG" "$OUT"
echo "Listo: $OUT"
