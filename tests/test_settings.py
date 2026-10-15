# SPDX-License-Identifier: GPL-3.0-or-later
import json

from quadrafall.settings import PRESETS, Settings


def test_saved_preset_picks_up_new_preset_values(tmp_path):
    # Ajustes guardados con una versión anterior de "NES+" (sin margen de fijado).
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"preset": "nes_plus", "rules": {"lock_delay": 0, "start_level": 7}}))
    settings = Settings(path).load()
    assert settings.rules["lock_delay"] == PRESETS["nes_plus"]["rules"]["lock_delay"] > 0
    assert settings.rules["start_level"] == 7          # lo que no es del estilo se respeta


def test_custom_settings_are_kept(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"preset": "custom", "rules": {"lock_delay": 45}}))
    assert Settings(path).load().rules["lock_delay"] == 45


def test_changing_a_rule_marks_custom_and_matching_marks_preset(tmp_path):
    settings = Settings(tmp_path / "s.json")
    settings.apply_preset("nes")
    settings.set_rule("das", 10)
    assert settings.data["preset"] == "custom"
    settings.set_rule("das", 16)
    assert settings.data["preset"] == "nes"
