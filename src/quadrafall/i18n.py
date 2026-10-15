# SPDX-License-Identifier: GPL-3.0-or-later
"""Traducciones. Para añadir un idioma: añade su código a LANGUAGES y una
columna más a cada entrada de STRINGS (en el mismo orden)."""

from __future__ import annotations

import locale
import os

LANGUAGES = ("es", "en")

STRINGS: dict[str, tuple[str, str]] = {
    # Menú principal
    "subtitle": ("Bloques que caen · software libre", "Falling blocks · free software"),
    "play": ("Jugar", "Play"),
    "mode": ("Modo", "Mode"),
    "mode_marathon": ("Maratón (A)", "Marathon (A)"),
    "mode_btype": ("25 líneas (B)", "25 lines (B)"),
    "mode_sprint": ("Sprint 40 líneas", "Sprint 40 lines"),
    "start_level": ("Nivel inicial", "Start level"),
    "garbage_rows": ("Filas prellenadas", "Pre-filled rows"),
    "options": ("Opciones", "Options"),
    "controls": ("Controles", "Controls"),
    "highscores": ("Récords", "High scores"),
    "quit": ("Salir", "Quit"),
    "back": ("Volver", "Back"),
    "menu_help": ("↑↓ elegir · ←→ cambiar · INTRO aceptar · ESC volver",
                  "↑↓ select · ←→ change · ENTER accept · ESC back"),
    "on": ("Sí", "On"),
    "off": ("No", "Off"),
    "frames": ("{n} fot.", "{n} f"),
    "instant": ("Instantáneo", "Instant"),
    # Opciones
    "gameplay": ("Jugabilidad", "Gameplay"),
    "appearance": ("Apariencia", "Appearance"),
    "sound": ("Sonido", "Sound"),
    "language": ("Idioma", "Language"),
    "lang_auto": ("Automático", "Automatic"),
    "lang_es": ("Español", "Español"),
    "lang_en": ("English", "English"),
    "preset": ("Estilo de juego", "Game style"),
    "preset_nes": ("NES clásico", "NES classic"),
    "preset_nes_plus": ("NES+ (recomendado)", "NES+ (recommended)"),
    "preset_modern": ("Moderno", "Modern"),
    "preset_custom": ("Personalizado", "Custom"),
    "rotation": ("Rotación", "Rotation"),
    "rot_nes": ("NES (sin ayudas)", "NES (no kicks)"),
    "rot_nes_plus": ("NES con ayudas", "NES with kicks"),
    "rot_srs": ("SRS (moderna)", "SRS (modern)"),
    "randomizer": ("Orden de piezas", "Randomizer"),
    "rand_nes": ("NES", "NES"),
    "rand_bag": ("Bolsa de 7", "7-bag"),
    "rand_random": ("Puro azar", "Pure random"),
    "hold_piece": ("Guardar pieza", "Hold piece"),
    "next_count": ("Piezas siguientes", "Next pieces"),
    "hard_drop": ("Caída instantánea", "Hard drop"),
    "ghost": ("Pieza fantasma", "Ghost piece"),
    "lock_delay": ("Retardo de fijado", "Lock delay"),
    "lock_nes": ("0 (NES)", "0 (NES)"),
    "das": ("Autodesplazamiento: espera", "Auto-shift delay (DAS)"),
    "arr": ("Autodesplazamiento: ritmo", "Auto-repeat rate (ARR)"),
    "soft_drop_speed": ("Velocidad bajada suave", "Soft drop speed"),
    "entry_delay": ("Retardo de aparición", "Entry delay"),
    "entry_nes": ("NES (10-18 fot.)", "NES (10-18 f)"),
    "line_clear_delay": ("Pausa al borrar líneas", "Line clear delay"),
    "garbage_density": ("Densidad de filas prellenadas", "Pre-filled density"),
    "theme": ("Tema", "Theme"),
    "theme_nes": ("NES", "NES"),
    "theme_classic": ("Clásico (Tango)", "Classic (Tango)"),
    "theme_modern": ("Neón", "Neon"),
    "theme_gameboy": ("Portátil verde", "Green handheld"),
    "theme_pastel": ("Pastel", "Pastel"),
    "theme_minimal": ("Minimalista", "Minimal"),
    "theme_colorblind": ("Apto para daltonismo", "Colorblind-friendly"),
    "block_style": ("Estilo de bloque", "Block style"),
    "style_nes": ("NES", "NES"),
    "style_bevel": ("Relieve", "Bevel"),
    "style_flat": ("Plano", "Flat"),
    "style_rounded": ("Redondeado", "Rounded"),
    "style_outline": ("Contorno", "Outline"),
    "font": ("Fuente", "Font"),
    "font_pixel": ("Píxel", "Pixel"),
    "font_smooth": ("Lisa", "Smooth"),
    "grid": ("Cuadrícula", "Grid"),
    "show_stats": ("Estadísticas de piezas", "Piece statistics"),
    "clear_anim": ("Animación de líneas", "Line clear animation"),
    "anim_nes": ("NES (columnas)", "NES (columns)"),
    "anim_flash": ("Destello", "Flash"),
    "anim_fade": ("Desvanecer", "Fade"),
    "quad_flash": ("Destello en cuádruple", "Flash on quad"),
    "callouts": ("Texto de jugadas", "Clear callouts"),
    "crt": ("Efecto televisor (CRT)", "CRT scanlines"),
    "fullscreen": ("Pantalla completa", "Fullscreen"),
    "sfx_volume": ("Volumen de efectos", "Effects volume"),
    "music_volume": ("Volumen de música", "Music volume"),
    "preview": ("VISTA PREVIA", "PREVIEW"),
    # Ayudas de opciones
    "help_preset": ("NES clásico: como el original. NES+: guardar pieza, varias siguientes y caída "
                    "instantánea. Moderno: reglas actuales.",
                    "NES classic: like the original. NES+: hold, several next pieces and hard drop. "
                    "Modern: current rules."),
    "help_rotation": ("Sin ayudas la pieza no gira si choca. Con ayudas se desplaza un poco para "
                      "poder girar.",
                      "Without kicks a blocked piece will not rotate. With kicks it shifts slightly "
                      "so it can rotate."),
    "help_randomizer": ("NES: puede haber rachas sin una pieza. Bolsa de 7: cada 7 piezas salen "
                        "las 7 distintas.",
                        "NES: droughts are possible. 7-bag: every 7 pieces contain all 7 shapes."),
    "help_lock_delay": ("Margen mínimo para mover la pieza cuando ya está apoyada, aunque bajes rápido. "
                        "0 = como el NES.",
                        "Minimum time to move a piece once it has landed, even when dropping fast. "
                        "0 = like the NES."),
    "help_das": ("Fotogramas con la dirección pulsada antes de que la pieza se desplace sola. NES: 16.",
                 "Frames holding a direction before auto-shift starts. NES: 16."),
    "help_arr": ("Fotogramas entre pasos del autodesplazamiento. NES: 6. 0 = hasta la pared.",
                 "Frames between auto-shift steps. NES: 6. 0 = straight to the wall."),
    "help_entry_delay": ("Pausa antes de que aparezca la siguiente pieza.",
                         "Pause before the next piece appears."),
    "help_garbage": ("Filas con bloques sueltos al empezar la partida, como en Quadrapassel.",
                     "Rows with scattered blocks at the start, like in Quadrapassel."),
    "help_crt": ("Simula las líneas de un televisor antiguo.", "Simulates an old TV's scanlines."),
    "help_density": ("Bloques por cada fila prellenada (de 10).", "Blocks per pre-filled row (out of 10)."),
    # Controles
    "act_left": ("Izquierda", "Left"),
    "act_right": ("Derecha", "Right"),
    "act_soft_drop": ("Bajar", "Soft drop"),
    "act_hard_drop": ("Caída instantánea", "Hard drop"),
    "act_rotate_cw": ("Girar a la derecha", "Rotate right"),
    "act_rotate_ccw": ("Girar a la izquierda", "Rotate left"),
    "act_hold": ("Guardar pieza", "Hold"),
    "act_pause": ("Pausa", "Pause"),
    "col_primary": ("Principal", "Primary"),
    "col_secondary": ("Secundaria", "Secondary"),
    "col_gamepad": ("Mando", "Gamepad"),
    "press_key": ("Pulsa una tecla... (ESC cancela)", "Press a key... (ESC cancels)"),
    "press_button": ("Pulsa un botón del mando... (ESC cancela)", "Press a gamepad button... (ESC cancels)"),
    "reset_controls": ("Restaurar controles", "Restore defaults"),
    "controls_help": ("INTRO cambiar · SUPR borrar · ESC volver", "ENTER change · DEL clear · ESC back"),
    "key_space": ("ESPACIO", "SPACE"),
    "key_return": ("INTRO", "ENTER"),
    "key_escape": ("ESC", "ESC"),
    "key_backspace": ("RETROCESO", "BACKSPACE"),
    "key_left shift": ("MAYÚS IZQ", "L-SHIFT"),
    "key_right shift": ("MAYÚS DER", "R-SHIFT"),
    "key_left ctrl": ("CTRL IZQ", "L-CTRL"),
    "key_right ctrl": ("CTRL DER", "R-CTRL"),
    "key_left alt": ("ALT", "ALT"),
    "key_right alt": ("ALT GR", "ALT GR"),
    "button": ("BOTÓN {n}", "BUTTON {n}"),
    "dpad": ("CRUCETA {d}", "D-PAD {d}"),
    "axis": ("PALANCA {n}{d}", "STICK {n}{d}"),
    "gamepad_connected": ("Mando conectado: {name}", "Gamepad connected: {name}"),
    # Partida
    "hold": ("GUARDADA", "HOLD"),
    "next": ("SIGUIENTE", "NEXT"),
    "statistics": ("ESTADÍSTICAS", "STATISTICS"),
    "lines": ("LÍNEAS", "LINES"),
    "lines_left": ("RESTAN", "LEFT"),
    "top": ("RÉCORD", "TOP"),
    "score": ("PUNTOS", "SCORE"),
    "level": ("NIVEL", "LEVEL"),
    "time": ("TIEMPO", "TIME"),
    "quads": ("CUÁDRUPLES", "QUADS"),
    "single": ("SIMPLE", "SINGLE"),
    "double": ("DOBLE", "DOUBLE"),
    "triple": ("TRIPLE", "TRIPLE"),
    "quad": ("¡CUÁDRUPLE!", "QUAD!"),
    "level_up": ("¡NIVEL {n}!", "LEVEL {n}!"),
    "paused": ("PAUSA", "PAUSED"),
    "resume": ("Continuar", "Resume"),
    "restart": ("Reiniciar", "Restart"),
    "quit_to_menu": ("Salir al menú", "Quit to menu"),
    "game_over": ("FIN DE LA PARTIDA", "GAME OVER"),
    "you_win": ("¡CONSEGUIDO!", "CLEARED!"),
    "new_record": ("¡NUEVO RÉCORD!", "NEW RECORD!"),
    "press_enter": ("Pulsa INTRO para continuar", "Press ENTER to continue"),
    "enter_name": ("Escribe tu nombre", "Enter your name"),
    "name": ("NOMBRE", "NAME"),
    "no_scores": ("Aún no hay récords en este modo", "No records in this mode yet"),
    "scores_help": ("←→ cambiar de modo · ESC volver", "←→ change mode · ESC back"),
    "player": ("JUGADOR", "PLAYER"),
}

_current = 0


def detect_language() -> str:
    candidates = [os.environ.get(v, "") for v in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")]
    try:
        candidates.append(locale.getlocale()[0] or "")
    except (ValueError, TypeError):
        pass
    for value in candidates:
        value = value.lower()
        if value.startswith(("es", "spanish")):
            return "es"
        if value:
            return "en"
    return "es"


def set_language(code: str) -> None:
    global _current
    if code == "auto" or code not in LANGUAGES:
        code = detect_language()
    _current = LANGUAGES.index(code)


def t(key: str, **params) -> str:
    entry = STRINGS.get(key)
    text = entry[_current] if entry else key
    return text.format(**params) if params else text


def has(key: str) -> bool:
    return key in STRINGS
