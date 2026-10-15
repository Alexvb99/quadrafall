# SPDX-License-Identifier: GPL-3.0-or-later
"""Coherencia de los temas: que ninguno quede a medias al añadir uno nuevo."""
import pytest

from quadrafall.engine.pieces import PIECES
from quadrafall.i18n import has
from quadrafall.ui.themes import BLOCK_STYLES, THEMES


@pytest.mark.parametrize("key", list(THEMES))
def test_theme_is_complete(key):
    theme = THEMES[key]
    assert theme.key == key
    assert has(f"theme_{key}"), "falta el nombre del tema en i18n.py"
    assert theme.default_style in BLOCK_STYLES
    if not theme.nes_levels:
        assert set(theme.pieces) == set(PIECES)


def _luminance(color):
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


@pytest.mark.parametrize("key", list(THEMES))
def test_pieces_stand_out_from_the_board(key):
    theme = THEMES[key]
    for kind in PIECES:
        for level in range(10):
            fill, _ = theme.block_colors(kind, level, "flat")
            assert abs(_luminance(fill) - _luminance(theme.board)) > 25, (kind, level)


def test_minimal_dark_mirrors_the_light_version():
    light, dark = THEMES["minimal"], THEMES["minimal_dark"]
    assert _luminance(dark.background) < 50 < 200 < _luminance(light.background)
    # El orden de contraste de las piezas se mantiene (la más marcada sigue siéndolo).
    by_contrast = lambda t: sorted(PIECES, key=lambda k: -abs(_luminance(t.pieces[k]) - _luminance(t.board)))  # noqa: E731
    assert by_contrast(light) == by_contrast(dark)
