# SPDX-License-Identifier: GPL-3.0-or-later
"""Generadores de la secuencia de piezas."""

from __future__ import annotations

import random

from .pieces import NES_ORDER, PIECES


class NESRandomizer:
    """Como el NES: elige al azar y, si sale la misma pieza que la anterior
    (o el valor "comodín"), vuelve a tirar una sola vez. Puede haber sequías."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.previous: str | None = None

    def next(self) -> str:
        roll = self.rng.randrange(8)
        if roll == 7 or NES_ORDER[roll] == self.previous:
            roll = self.rng.randrange(7)
        piece = NES_ORDER[roll]
        self.previous = piece
        return piece


class BagRandomizer:
    """Bolsa de 7: cada grupo de siete piezas contiene una de cada tipo."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.bag: list[str] = []

    def next(self) -> str:
        if not self.bag:
            self.bag = list(PIECES)
            self.rng.shuffle(self.bag)
        return self.bag.pop()


class PureRandomizer:
    """Totalmente aleatorio, sin ninguna corrección."""

    def __init__(self, rng: random.Random):
        self.rng = rng

    def next(self) -> str:
        return self.rng.choice(PIECES)


RANDOMIZERS = {
    "nes": NESRandomizer,
    "bag": BagRandomizer,
    "random": PureRandomizer,
}
