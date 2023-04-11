import unittest

from src.model import Board
from src.model.dataclasses import Position, Side


class BoardTest(unittest.TestCase):
    def test_delete_piece(self):
        board = Board()
        board.set_initial_positions()
        assert board.get_piece(Position(0, 1)) is not None
        board.delete_piece(board.get_piece(Position(0, 1)))
        assert board.get_piece(Position(0, 1)) is None

    def test_update_piece_position(self):
        board = Board()
        board.set_initial_positions()
        assert board.get_piece(Position(0, 1)) is not None
        board.update_piece_position(board.get_piece(Position(0, 1)), Position(0, 2))
        assert board.get_piece(Position(0, 1)) is None
        assert board.get_piece(Position(0, 2)) is not None

    def test_get_piece(self):
        board = Board()
        board.set_initial_positions()
        assert board.get_piece(Position(0, 0)) is None
        assert board.get_piece(Position(0, 1)) is not None
        assert board.get_piece(Position(0, 2)) is None

    def test_get_pieces(self):
        board = Board()
        board.set_initial_positions()
        assert len(board.get_pieces(Side.WHITE)) == 12
        assert len(board.get_pieces(Side.BLACK)) == 12

    def test_get_piece_between(self):
        board = Board()
        board.set_initial_positions()
        assert board.get_piece_between(Position(0, 1), Position(2, 3)) is not None
        assert board.get_piece_between(Position(0, 1), Position(2, 1)) is None


if __name__ == '__main__':
    unittest.main()
