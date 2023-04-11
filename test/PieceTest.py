import unittest

from src.model.dataclasses import Piece, Side, Position


class PieceTest(unittest.TestCase):
    def test_get_possible_moves(self):
        piece = Piece(Side.BLACK, Position(0, 1))
        assert set(piece.get_possible_moves()) == {Position(1, 0), Position(1, 2)}

    def test_get_possible_moves_with_long_jump(self):
        piece = Piece(Side.BLACK, Position(0, 2))
        assert set(piece.get_possible_moves(True)) == {Position(2, 0), Position(2, 4)}

    def test_get_possible_moves_with_king(self):
        piece = Piece(Side.BLACK, Position(1, 1), True)
        assert set(piece.get_possible_moves()) == {Position(0, 0), Position(0, 2), Position(2, 0), Position(2, 2)}

    def test_get_possible_moves_with_king_and_long_jump(self):
        piece = Piece(Side.BLACK, Position(2, 2), True)
        assert set(piece.get_possible_moves(True)) == {Position(0, 0), Position(0, 4), Position(4, 0), Position(4, 4)}
    def test_distance_from_edge(self):
        piece = Piece(Side.BLACK, Position(0, 0))
        assert piece.distance_from_edge() == 7
        piece = Piece(Side.BLACK, Position(1, 0))
        assert piece.distance_from_edge() == 6
        piece = Piece(Side.WHITE, Position(7, 0))
        assert piece.distance_from_edge() == 7
        piece = Piece(Side.WHITE, Position(6, 0))
        assert piece.distance_from_edge() == 6

if __name__ == '__main__':
    unittest.main()
