#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Crea el paquete de Arch Linux a partir de dist/Quadrafall-<versión>-Linux-x86_64.tar.gz
# (lo genera packaging/linux/build.sh):
#   dist/quadrafall-bin-<versión>-<pkgrel>-x86_64.pkg.tar.zst
#   dist/PKGBUILD   (con la versión y las sumas de esta compilación)
# Requiere Arch Linux con base-devel y pacman-contrib (updpkgsums). No se ejecuta como root.
# Uso: build.sh <versión>
set -eu
cd "$(dirname "$0")/../.."

VERSION="$1"
APP_ID=io.github.alexvb99.Quadrafall
B=build/arch
rm -rf "$B"
mkdir -p "$B"

# Versión nueva: pkgrel vuelve a 1. Misma versión: se respeta el pkgrel del repositorio.
if grep -q "^pkgver=$VERSION\$" packaging/arch/PKGBUILD; then
    cp packaging/arch/PKGBUILD "$B/PKGBUILD"
else
    sed "s/^pkgver=.*/pkgver=$VERSION/; s/^pkgrel=.*/pkgrel=1/" packaging/arch/PKGBUILD > "$B/PKGBUILD"
fi

# Fuentes locales con los nombres que espera el PKGBUILD: makepkg no las descarga y las sumas
# coinciden con los archivos que se publican.
cp "dist/Quadrafall-$VERSION-Linux-x86_64.tar.gz" "$B/"
for EXT in desktop png metainfo.xml; do
    cp "packaging/linux/$APP_ID.$EXT" "$B/$APP_ID-$VERSION.$EXT"
done

# -d: las dependencias solo hacen falta para jugar, no para empaquetar.
(cd "$B" && updpkgsums && makepkg -f -d --noconfirm)
cp "$B"/quadrafall-bin-*.pkg.tar.zst "$B/PKGBUILD" dist/
echo "Listo: $(ls dist/quadrafall-bin-*.pkg.tar.zst)"
