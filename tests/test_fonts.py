# SPDX-License-Identifier: GPL-3.0-or-later
"""Las fuentes incluidas existen, llevan su licencia y cubren el español."""
import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402
import pytest  # noqa: E402

from quadrafall.paths import asset_path  # noqa: E402
from quadrafall.ui.font import FONTS, Text  # noqa: E402

SPANISH = "ÁÉÍÓÚÑÜáéíóúñü¿¡·%:"


@pytest.fixture(scope="module", autouse=True)
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


@pytest.mark.parametrize("kind", [k for k, v in FONTS.items() if v[0]])
def test_bundled_font_has_file_and_license(kind):
    filename = FONTS[kind][0]
    assert asset_path("fonts/" + filename).is_file()
    family = filename.split("-")[0]
    assert asset_path(f"fonts/OFL-{family}.txt").is_file()


@pytest.mark.parametrize("kind", list(FONTS))
def test_font_covers_spanish_without_fallback(kind):
    font = Text(kind).font
    assert all(not missing for missing, _ in font._runs(SPANISH))


@pytest.mark.parametrize("kind", list(FONTS))
def test_missing_glyphs_fall_back_to_bitmap_arrows(kind):
    text = Text(kind)
    # Las flechas no están en las fuentes: deben dibujarse igualmente (con ancho).
    assert text.size("←→", 3)[0] > 10
    assert text.size("A ← B", 3)[0] > text.size("A  B", 3)[0]
