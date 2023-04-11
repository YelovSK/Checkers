import unittest
from src.model import Game, Board
from src.model.dataclasses import Position, Move, Side

class IsValidMove(unittest.TestCase):
    def test_is_move_valid_from_edge(self):
        game = Game()
        # Trying to move a piece from the edge of the board
        assert game.is_move_valid(Position(5, 0), Position(4, 1)) == True
        assert game.is_move_valid(Position(2, 7), Position(3, 6)) == True

    def test_is_move_valid_no_piece(self):
        game = Game()
        # Trying to move an empty cell
        assert game.is_move_valid(Position(0, 0), Position(1, 1)) == False
        assert game.is_move_valid(Position(7, 7), Position(6, 6)) == False

    def test_is_move_valid_to_occupied(self):
        game = Game()
        # Trying to move to a cell that is not empty
        assert game.is_move_valid(Position(0, 1), Position(1, 0)) == False
        assert game.is_move_valid(Position(7, 6), Position(6, 7)) == False

    def test_is_move_valid_over_enemy(self):
        game = Game()
        game.board.update_piece_position(game.board.get_piece(Position(5, 0)), Position(3, 2))
        # Move over an enemy piece
        assert game.is_move_valid(Position(2, 1), Position(4, 3)) == True

    def test_is_move_valid_over_own(self):
        game = Game()
        # Move over an own piece
        assert game.is_move_valid(Position(1, 0), Position(3, 2)) == False

    def test_is_move_valid_over_empty(self):
        game = Game()
        # Move over an empty cell
        assert game.is_move_valid(Position(2, 1), Position(4, 3)) == False



class GetValidMoves(unittest.TestCase):

    def test_get_valid_moves_of_piece(self):
        game = Game()
        # Empty field
        moves = game.get_valid_moves(game.board.get_piece(Position(2, 1)))
        assert Position(3, 0) in moves and Position(3, 2) in moves

    def test_get_valid_moves_of_piece_with_enemy(self):
        game = Game()
        enemy_pos = Position(3, 2)
        game.board.update_piece_position(game.board.get_piece(Position(5, 0)), enemy_pos)
        moves = game.get_valid_moves(game.board.get_piece(Position(2, 1)))
        # Move over an enemy piece
        assert Position(3, 0) in moves \
               and Position(4, 3) in moves \
               and enemy_pos not in moves

    def test_get_valid_moves_over_multiple(self):
        game = Game()
        game.board.delete_piece(game.board.get_piece(Position(6, 1)))
        assert game.board.get_piece(Position(6, 1)) is None
        game.board.update_piece_position(game.board.get_piece(Position(5, 0)), Position(3, 2))
        # Move over multiple enemy pieces
        assert Position(6, 1) in game.get_valid_moves(game.board.get_piece(Position(2, 1))).keys()


class ApplyMove(unittest.TestCase):
    def test_apply_move(self):
        game = Game()
        from_pos, to_pos = Position(2, 1), Position(3, 0)
        before_side = game.side_to_move
        move = Move(game.board.get_piece(from_pos), to_pos, [])
        game.apply_move(move)
        assert game.board.get_piece(to_pos) is not None
        assert game.board.get_piece(from_pos) is None
        assert game.side_to_move != before_side


    def test_apply_move_over_enemy(self):
        game = Game()
        game.board.update_piece_position(game.board.get_piece(Position(5, 0)), Position(3, 2))
        from_pos, enemy_pos, to_pos = Position(2, 1), Position(3, 2), Position(4, 3)
        before_side = game.side_to_move
        move = Move(game.board.get_piece(from_pos), to_pos, [game.board.get_piece(enemy_pos)])
        game.apply_move(move)
        assert game.board.get_piece(to_pos) is not None
        assert game.board.get_piece(from_pos) is None
        assert game.board.get_piece(enemy_pos) is None
        assert game.side_to_move != before_side

class GetBestMove(unittest.TestCase):
    def test_get_best_move(self):
        game = Game()
        game.board.update_piece_position(game.board.get_piece(Position(5, 0)), Position(3, 2))
        game.board.delete_piece(game.board.get_piece(Position(6, 1)))
        from_pos, to_pos, first_enemy_pos, second_enemy_pos = Position(2, 1), Position(6, 1), Position(4, 3), Position(5, 2)

        best_move = game.get_best_move(list(game.get_valid_moves(game.board.get_piece(from_pos)).values()))
        assert best_move.from_piece.position == from_pos
        assert best_move.to_position == to_pos

class GetWinner(unittest.TestCase):
    def test_get_winner(self):
        game = Game()
        for piece in game.board.get_pieces(Side.WHITE):
            game.board.delete_piece(piece)
        assert game.get_winner() == Side.BLACK

if __name__ == '__main__':
    unittest.main()

