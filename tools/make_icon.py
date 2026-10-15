# SPDX-License-Identifier: GPL-3.0-or-later
"""Genera el icono del juego (PNG para Linux/ventana e ICO para Windows).

Uso:  python tools/make_icon.py
"""

from __future__ import annotations

import io
import os
import struct
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PNG_OUT = ROOT / "src" / "quadrafall" / "assets" / "icon.png"
ICO_OUT = ROOT / "packaging" / "windows" / "icon.ico"
LINUX_OUT = ROOT / "packaging" / "linux" / "io.github.alexvb99.Quadrafall.png"

BG = (28, 28, 40)
FRAME = (124, 124, 140)
BLUE = (0, 88, 248)
SKY = (60, 188, 252)
WHITE = (252, 252, 252)


def block(surf, x, y, size, color, white_center=False):
    s = size // 8
    r = pygame.Rect(x, y, size - s, size - s)
    surf.fill(color, r)
    if white_center:
        surf.fill(WHITE, r.inflate(-2 * s, -2 * s))
        surf.fill(WHITE, (r.x, r.y, s, s))
    else:
        surf.fill(WHITE, (r.x, r.y, s, s))
        surf.fill(WHITE, (r.x + s, r.y + s, 2 * s, s))
        surf.fill(WHITE, (r.x + s, r.y + 2 * s, s, s))


def draw_icon(size: int = 256) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    radius = size // 6
    pygame.draw.rect(surf, BG, surf.get_rect(), border_radius=radius)
    pygame.draw.rect(surf, FRAME, surf.get_rect(), width=max(2, size // 32), border_radius=radius)
    c = size // 6   # tamaño de celda: rejilla de 4x4 centrada
    ox = oy = (size - 4 * c) // 2
    # Pieza T (blanca, como en el NES) arriba, y una pila debajo
    for gx, gy in ((0, 0), (1, 0), (2, 0), (1, 1)):
        block(surf, ox + gx * c, oy + gy * c, c, BLUE, white_center=True)
    for gx, gy in ((0, 2), (0, 3), (1, 3), (3, 2)):
        block(surf, ox + gx * c, oy + gy * c, c, SKY)
    for gx, gy in ((2, 3), (3, 3), (3, 1)):
        block(surf, ox + gx * c, oy + gy * c, c, BLUE)
    return surf


def png_bytes(surf: pygame.Surface) -> bytes:
    buffer = io.BytesIO()
    pygame.image.save(surf, buffer, "icon.png")
    return buffer.getvalue()


def write_ico(path: Path, big: pygame.Surface, sizes=(256, 128, 64, 48, 32, 16)) -> None:
    """ICO con imágenes PNG embebidas (válido desde Windows Vista)."""
    images = [png_bytes(big if s == big.get_width() else pygame.transform.smoothscale(big, (s, s)))
              for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries = b""
    for s, data in zip(sizes, images):
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    path.write_bytes(header + entries + b"".join(images))


def main() -> None:
    pygame.init()
    icon = draw_icon(256)
    for out in (PNG_OUT, ICO_OUT, LINUX_OUT):
        out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(icon, str(PNG_OUT))
    pygame.image.save(icon, str(LINUX_OUT))
    write_ico(ICO_OUT, icon)
    print(f"Iconos generados:\n  {PNG_OUT}\n  {LINUX_OUT}\n  {ICO_OUT}")


if __name__ == "__main__":
    main()
