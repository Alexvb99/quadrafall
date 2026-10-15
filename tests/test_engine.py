# SPDX-License-Identifier: GPL-3.0-or-later
import random

import pytest

from quadrafall.engine.board import Board
from quadrafall.engine.game import (Action, ActivePiece, Game, GameRules, gravity_frames,
                                    level_for_lines, nes_entry_delay)
from quadrafall.engine.pieces import PIECES, ROTATION_SYSTEMS
from quadrafall.engine.randomizer import BagRandomizer, NESRandomizer

NOTHING = frozenset()


def step(game, frames=1, held=NOTHING, pressed=NOTHING):
    for i in range(frames):
        game.update(frozenset(held), frozenset(pressed) if i == 0 else NOTHING)


def make_game(**rules):
    defaults = dict(entry_delay=0, line_clear_frames=0)
    defaults.update(rules)
    return Game(GameRules(**defaults), seed=1)


# --- piezas y rotación ---------------------------------------------------------

def test_every_shape_has_four_cells():
    for system in ROTATION_SYSTEMS.values():
        for kind in PIECES:
            for r in range(system.states(kind)):
                assert len(set(system.shape(kind, r))) == 4


def test_nes_t_spawns_pointing_down_and_rotates_around_pivot():
    nes = ROTATION_SYSTEMS["nes"]
    assert set(nes.shape("T", 0)) == {(-1, 0), (0, 0), (1, 0), (0, 1)}
    assert set(nes.shape("T", 1)) == {(0, -1), (-1, 0), (0, 0), (0, 1)}  # apunta a la izquierda
    assert nes.states("S") == nes.states("Z") == nes.states("I") == 2
    assert nes.states("O") == 1


def test_srs_i_rotates_inside_its_box():
    srs = ROTATION_SYSTEMS["srs"]
    assert set(srs.shape("I", 1)) == {(2, 0), (2, 1), (2, 2), (2, 3)}


@pytest.mark.parametrize("rotation,expected", [("nes", False), ("nes_plus", True), ("srs", True)])
def test_wall_kicks_depend_on_rotation_system(rotation, expected):
    game = make_game(rotation=rotation)
    # I vertical pegada a la pared derecha: al girar a horizontal se saldría.
    system = game.system
    if rotation == "srs":
        game.piece = ActivePiece("I", 1, 7, 10)    # columna x+2 = 9
    else:
        game.piece = ActivePiece("I", 1, 9, 10)
    assert max(x for x, _ in game.piece_cells()) == 9
    assert game._try_rotate(1 if rotation != "srs" else 1) is expected
    assert system.name == rotation


# --- tablero -------------------------------------------------------------------

def test_clear_rows_shifts_everything_down():
    board = Board()
    board.cells[-1] = ["I"] * 10
    board.cells[-2][0] = "T"
    assert board.full_rows() == [board.height - 1]
    board.clear_rows(board.full_rows())
    assert board.cells[-1][0] == "T"
    assert all(c is None for c in board.cells[0])


def test_garbage_always_leaves_a_hole():
    board = Board()
    board.add_garbage(8, 9, random.Random(3))
    for row in board.cells[-8:]:
        assert row.count(None) == 1
    assert board.stack_height() == 8


# --- reglas NES -------------------------------------------------------------------

def test_gravity_table():
    assert gravity_frames(0) == 48
    assert gravity_frames(9) == 6
    assert gravity_frames(18) == 3
    assert gravity_frames(19) == 2
    assert gravity_frames(29) == 1


def test_level_progression_matches_nes():
    assert level_for_lines(0, 9) == 0
    assert level_for_lines(0, 10) == 1
    assert level_for_lines(9, 99) == 9
    assert level_for_lines(9, 100) == 10
    assert level_for_lines(18, 129) == 18
    assert level_for_lines(18, 130) == 19
    assert level_for_lines(19, 140) == 20


def test_nes_entry_delay():
    assert nes_entry_delay(1) == 10
    assert nes_entry_delay(3) == 12
    assert nes_entry_delay(7) == 14
    assert nes_entry_delay(20) == 18


def test_four_lines_score_1200_times_level_plus_one():
    game = make_game(start_level=2, hard_drop=True, rotation="nes")
    for y in range(game.board.height - 4, game.board.height):
        game.board.cells[y] = ["J"] * 9 + [None]
    game.piece = ActivePiece("I", 1, 9, 5)       # vertical sobre el hueco
    step(game, pressed={Action.HARD_DROP})
    assert game.lines == 4
    assert game.tetris_lines == 4
    assert game.score >= 1200 * 3
    assert game.stats  # sigue jugando
    assert not game.finished


def test_gravity_moves_piece_down_at_level_speed():
    game = make_game(start_level=0)
    y = game.piece.y
    step(game, 47)
    assert game.piece.y == y
    step(game, 1)
    assert game.piece.y == y + 1


def test_soft_drop_scores_one_point_per_row():
    game = make_game(soft_drop_frames=2)
    step(game, 10, held={Action.SOFT_DROP})
    assert game.score == 5


def test_nes_lock_happens_on_gravity_tick_without_lock_delay():
    game = make_game(lock_delay=0, start_level=0)
    game.piece.y += game.drop_distance()
    kind = game.piece.kind
    step(game, 47)
    assert game.piece is not None and game.piece.kind == kind
    step(game, 1)
    assert sum(c is not None for row in game.board.cells for c in row) == 4


def test_das_initial_move_then_autorepeat():
    game = make_game(das=16, arr=6, start_level=0)
    x = game.piece.x
    step(game, 1, held={Action.RIGHT}, pressed={Action.RIGHT})
    assert game.piece.x == x + 1
    step(game, 15, held={Action.RIGHT})
    assert game.piece.x == x + 1
    step(game, 1, held={Action.RIGHT})
    assert game.piece.x == x + 2
    step(game, 6, held={Action.RIGHT})
    assert game.piece.x == x + 3


def test_arr_zero_moves_straight_to_wall():
    game = make_game(das=5, arr=0)
    step(game, 6, held={Action.LEFT}, pressed={Action.LEFT})
    assert min(x for x, _ in game.piece_cells()) == 0


def test_hold_only_once_per_piece():
    game = make_game(hold=True)
    first = game.piece.kind
    step(game, pressed={Action.HOLD})
    assert game.held == first
    second = game.piece.kind
    step(game, pressed={Action.HOLD})
    assert game.piece.kind == second            # bloqueado hasta fijar
    step(game, pressed={Action.HARD_DROP})
    step(game, 2)
    step(game, pressed={Action.HOLD})
    assert game.held != first or game.piece.kind == first


def test_hold_disabled_does_nothing():
    game = make_game(hold=False)
    kind = game.piece.kind
    step(game, pressed={Action.HOLD})
    assert game.held is None and game.piece.kind == kind


def test_game_over_when_spawn_is_blocked():
    game = make_game()
    for y in range(game.board.hidden, game.board.hidden + 3):
        game.board.cells[y] = [None] + ["Z"] * 9    # con hueco: no se borran
    step(game, pressed={Action.HARD_DROP})
    step(game, 3)
    assert game.state == "over"
    assert "game_over" in game.events or game.finished


def _column_wall(game, top_row):
    """Rellena la columna 0 desde `top_row` hasta abajo (sin completar líneas)."""
    for y in range(top_row, game.board.height):
        game.board.cells[y][0] = "L"


def test_piece_sticking_out_above_the_limit_loses():
    # Una I vertical que queda apoyada sobresaliendo por arriba (p. ej. girada en el
    # último momento) debe acabar la partida aunque la siguiente pieza quepa.
    game = make_game(rotation="nes")
    _column_wall(game, game.board.hidden + 2)
    game.piece = ActivePiece("I", 1, 0, 2)          # filas 0-3: dos de ellas ocultas
    step(game, pressed={Action.HARD_DROP})
    assert any(c is not None for row in game.board.cells[: game.board.hidden] for c in row)
    assert game.state == "over"


def test_piece_touching_the_top_row_but_visible_does_not_lose():
    game = make_game(rotation="nes")
    _column_wall(game, game.board.hidden + 4)
    game.piece = ActivePiece("I", 1, 0, 2)          # cae hasta las filas 2-5, todas visibles
    step(game, pressed={Action.HARD_DROP})
    assert game.state != "over"


def test_lines_cleared_can_save_a_piece_sticking_out():
    # Si la pieza completa líneas y al bajar todo queda dentro, se sigue jugando.
    game = make_game(rotation="nes")
    board = game.board
    for y in (board.hidden, board.hidden + 1):
        board.cells[y] = [None] + ["J"] * 9
    _column_wall(game, board.hidden + 2)
    game.piece = ActivePiece("I", 1, 0, 2)          # filas 0-3: completa las filas 2 y 3
    step(game, pressed={Action.HARD_DROP})
    assert game.lines == 2
    assert game.state != "over"


def test_lock_grace_lets_you_slide_after_fast_drop():
    game = make_game(lock_delay=20, soft_drop_frames=2)
    game.piece.y += game.drop_distance()
    kind = game.piece.kind
    step(game, 19, held={Action.SOFT_DROP})
    assert game.piece is not None and game.piece.kind == kind
    step(game, 1, held={Action.SOFT_DROP})
    assert sum(c is not None for row in game.board.cells for c in row) == 4


def test_nes_soft_drop_locks_almost_immediately():
    game = make_game(lock_delay=0, lock_resets=0, soft_drop_frames=2)
    game.piece.y += game.drop_distance()
    step(game, 2, held={Action.SOFT_DROP})
    assert sum(c is not None for row in game.board.cells for c in row) == 4


def test_moving_on_the_ground_resets_the_grace_a_limited_number_of_times():
    game = make_game(lock_delay=20, lock_resets=2, das=100, start_level=19)
    game.piece.y += game.drop_distance()
    for direction in (Action.LEFT, Action.RIGHT):
        step(game, 15)
        step(game, 1, held={direction}, pressed={direction})   # reinicia el margen
    step(game, 15)
    assert game.piece is not None                                # sigue viva
    step(game, 1, held={Action.LEFT}, pressed={Action.LEFT})    # ya no reinicia
    step(game, 5)
    assert sum(c is not None for row in game.board.cells for c in row) == 4


def test_btype_ends_when_goal_reached():
    game = make_game(mode="btype", rotation="nes")
    game.lines = 24
    game.board.cells[-1] = ["L"] * 9 + [None]
    game.piece = ActivePiece("I", 1, 9, 10)
    step(game, pressed={Action.HARD_DROP})
    assert game.state == "won"


# --- generadores ------------------------------------------------------------------

def test_bag_contains_each_piece_once_per_seven():
    bag = BagRandomizer(random.Random(5))
    for _ in range(10):
        assert sorted(bag.next() for _ in range(7)) == sorted(PIECES)


def test_nes_randomizer_repeats_less_than_pure_chance():
    rnd = NESRandomizer(random.Random(9))
    seq = [rnd.next() for _ in range(7000)]
    repeats = sum(a == b for a, b in zip(seq, seq[1:])) / len(seq)
    assert repeats < 1 / 7 * 0.5
    assert set(seq) == set(PIECES)
