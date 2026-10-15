# SPDX-License-Identifier: GPL-3.0-or-later
"""Efectos y música de 8 bits generados por código: no hay archivos de audio
que licenciar. La melodía es «Korobeiniki», canción popular rusa del siglo XIX
(dominio público); el arreglo es propio de este proyecto."""

from __future__ import annotations

import random
import threading
from array import array

import pygame

NOTE_INDEX = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
              "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}


def note_freq(name: str) -> float:
    """'A4' -> 440 Hz."""
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE_INDEX[pitch] + (octave - 4) * 12) / 12)


class Synth:
    def __init__(self, rate: int):
        self.rate = rate
        self.noise = random.Random(7)

    def tone(self, freq: float, ms: float, wave: str = "square", volume: float = 0.3,
             duty: float = 0.5, slide: float = 0.0, decay: bool = True) -> list[float]:
        n = int(self.rate * ms / 1000)
        if not decay and not slide and wave != "noise" and freq > 0:
            return self._sustained(freq, n, wave, volume, duty)
        out = [0.0] * n
        phase = 0.0
        for i in range(n):
            f = freq + slide * i / max(1, n)
            phase = (phase + f / self.rate) % 1.0
            if wave == "square":
                v = 1.0 if phase < duty else -1.0
            elif wave == "triangle":
                v = 4 * phase - 1 if phase < 0.5 else 3 - 4 * phase
            else:  # ruido
                v = self.noise.uniform(-1, 1)
            env = (1 - i / n) if decay else min(1.0, (n - i) / (self.rate * 0.01))
            out[i] = v * volume * env
        return out

    def _sustained(self, freq: float, n: int, wave: str, volume: float, duty: float) -> list[float]:
        """Vía rápida para notas sostenidas: repite un único periodo de onda."""
        period = max(2, round(self.rate / freq))
        if wave == "square":
            high = max(1, int(period * duty))
            cycle = [volume] * high + [-volume] * (period - high)
        else:
            half = period / 2
            cycle = [volume * ((4 * i / period - 1) if i < half else (3 - 4 * i / period)) for i in range(period)]
        out = (cycle * (n // period + 1))[:n]
        fade = min(n, int(self.rate * 0.004))  # rampa corta para evitar chasquidos
        for i in range(fade):
            out[n - 1 - i] *= i / fade
        return out

    def seq(self, *parts: list[float]) -> list[float]:
        result: list[float] = []
        for part in parts:
            result.extend(part)
        return result


def _sound_effects(s: Synth) -> dict[str, list[float]]:
    return {
        "move": s.tone(880, 22, duty=0.25, volume=0.18),
        "rotate": s.tone(1180, 35, duty=0.25, volume=0.2, slide=300),
        "lock": s.seq(s.tone(0, 45, wave="noise", volume=0.25)),
        "hard_drop": s.seq(s.tone(160, 30, volume=0.3, slide=-80), s.tone(0, 50, wave="noise", volume=0.3)),
        "hold": s.seq(s.tone(660, 30, duty=0.25, volume=0.2), s.tone(990, 40, duty=0.25, volume=0.2)),
        "clear1": s.seq(s.tone(note_freq("C5"), 50), s.tone(note_freq("E5"), 70)),
        "clear2": s.seq(s.tone(note_freq("C5"), 45), s.tone(note_freq("E5"), 45), s.tone(note_freq("G5"), 70)),
        "clear3": s.seq(*(s.tone(note_freq(n), 45) for n in ("C5", "E5", "G5")), s.tone(note_freq("C6"), 80)),
        "clear4": s.seq(*(s.tone(note_freq(n), 50, volume=0.32) for n in ("C5", "E5", "G5", "C6", "E6")),
                        s.tone(note_freq("G6"), 220, volume=0.32)),
        "level_up": s.seq(*(s.tone(note_freq(n), 60, duty=0.25) for n in ("G5", "A5", "B5")),
                          s.tone(note_freq("D6"), 160, duty=0.25)),
        "game_over": s.seq(*(s.tone(note_freq(n), 140, wave="triangle", volume=0.4)
                             for n in ("E5", "D5", "C5", "B4", "A4")), s.tone(note_freq("E4"), 500, wave="triangle", volume=0.4)),
        "won": s.seq(*(s.tone(note_freq(n), 90, volume=0.3) for n in ("C5", "E5", "G5", "C6", "G5")),
                     s.tone(note_freq("C6"), 400, volume=0.3)),
        "menu_move": s.tone(700, 18, duty=0.25, volume=0.12),
        "menu_select": s.seq(s.tone(880, 30, duty=0.25, volume=0.18), s.tone(1320, 50, duty=0.25, volume=0.18)),
        "pause": s.seq(s.tone(note_freq("E6"), 40, volume=0.15), s.tone(note_freq("B5"), 60, volume=0.15)),
    }


# (nota, pulsos). "R" = silencio. Un pulso = una negra.
_MELODY_A = [
    ("E5", 1), ("B4", .5), ("C5", .5), ("D5", 1), ("C5", .5), ("B4", .5),
    ("A4", 1), ("A4", .5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5),
    ("B4", 1.5), ("C5", .5), ("D5", 1), ("E5", 1),
    ("C5", 1), ("A4", 1), ("A4", 1), ("R", 1),
    ("D5", 1.5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5),
    ("E5", 1.5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5),
    ("B4", 1), ("B4", .5), ("C5", .5), ("D5", 1), ("E5", 1),
    ("C5", 1), ("A4", 1), ("A4", 1), ("R", 1),
]
_MELODY_B = [
    ("E5", 2), ("C5", 2), ("D5", 2), ("B4", 2), ("C5", 2), ("A4", 2), ("G#4", 2), ("B4", 2),
    ("E5", 2), ("C5", 2), ("D5", 2), ("B4", 2), ("C5", 1), ("E5", 1), ("A5", 2), ("G#5", 4),
]
# Bajo: nota fundamental por compás, rebotando entre octavas en corcheas.
_BASS_A = ["E2", "A2", "E2", "A2", "D2", "C2", "E2", "A2"]
_BASS_B = ["A2", "E2", "A2", "E2", "A2", "E2", "A2", "E2"]


def _music(s: Synth, bpm: float = 140) -> list[float]:
    beat = 60_000 / bpm
    melody = _MELODY_A + _MELODY_A + _MELODY_B
    lead: list[float] = []
    for note, beats in melody:
        ms = beats * beat
        if note == "R":
            lead.extend([0.0] * int(s.rate * ms / 1000))
        else:
            lead.extend(s.tone(note_freq(note), ms * 0.92, duty=0.5, volume=0.16, decay=False))
            lead.extend([0.0] * int(s.rate * ms * 0.08 / 1000))
    bass: list[float] = []
    for root in _BASS_A + _BASS_A + _BASS_B:
        low = note_freq(root)
        for i in range(8):
            bass.extend(s.tone(low * (2 if i % 2 else 1), beat / 2, wave="triangle", volume=0.22, decay=False))
    n = min(len(lead), len(bass))
    return [lead[i] + bass[i] for i in range(n)]


class Audio:
    def __init__(self):
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.music: pygame.mixer.Sound | None = None
        self.music_channel: pygame.mixer.Channel | None = None
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self._want_music = False
        self._music_pcm: bytes | None = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            rate, fmt, channels = pygame.mixer.get_init()
            if fmt != -16:
                return
        except pygame.error:
            return
        self.enabled = True
        self.rate, self.channels = rate, channels
        pygame.mixer.set_num_channels(16)
        pygame.mixer.set_reserved(1)
        self.music_channel = pygame.mixer.Channel(0)
        synth = Synth(rate)
        self.sounds = {name: self._to_sound(data) for name, data in _sound_effects(synth).items()}
        self.set_volumes(self.sfx_volume, self.music_volume)
        # La música tarda un poco en generarse: se calcula en segundo plano, pero ese
        # hilo no toca pygame (si el juego se cierra mientras tanto, pygame podría
        # estar ya cerrado). El bucle principal la recoge en update().
        threading.Thread(target=self._build_music, daemon=True).start()

    def _to_pcm(self, samples: list[float]) -> bytes:
        mono = array("h", [int(v * 32767) for v in samples])  # |v| < 1 en todos los sonidos
        if self.channels == 1:
            return mono.tobytes()
        data = array("h", bytes(2 * len(mono) * self.channels))
        for ch in range(self.channels):
            data[ch::self.channels] = mono
        return data.tobytes()

    def _to_sound(self, samples: list[float]) -> pygame.mixer.Sound:
        return pygame.mixer.Sound(buffer=self._to_pcm(samples))

    def _build_music(self) -> None:
        """Hilo secundario: solo cálculo en Python puro."""
        self._music_pcm = self._to_pcm(_music(Synth(self.rate)))

    def update(self) -> None:
        """Llamar en cada fotograma desde el hilo principal."""
        if self.music is None and self._music_pcm is not None:
            try:
                self.music = pygame.mixer.Sound(buffer=self._music_pcm)
                self.music.set_volume(self.music_volume)
            except pygame.error:
                self.enabled = False
            self._music_pcm = None
            if self._want_music:
                self.play_music()

    def set_volumes(self, sfx: float, music: float) -> None:
        self.sfx_volume, self.music_volume = sfx, music
        for sound in self.sounds.values():
            sound.set_volume(sfx)
        if self.music:
            self.music.set_volume(music)

    def play(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound and self.sfx_volume > 0:
            sound.play()

    def play_music(self) -> None:
        self._want_music = True
        if self.enabled and self.music and self.music_volume > 0 and not self.music_channel.get_busy():
            self.music_channel.play(self.music, loops=-1)

    def stop_music(self) -> None:
        self._want_music = False
        if self.enabled and self.music_channel:
            self.music_channel.stop()

    def pause_music(self, paused: bool) -> None:
        if self.enabled and self.music_channel:
            if paused:
                self.music_channel.pause()
            else:
                self.music_channel.unpause()
