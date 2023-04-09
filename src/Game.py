from __future__ import annotations

import datetime
import random

from src.model.Board import Board
from src.model.Constants import BOARD_SIZE
from src.model.dataclasses import Side, Position, Move, Piece


class Game:
    def __init__(self):
        self.board = Board()
        self.board.set_initial_positions()
        self.side_to_move = Side.BLACK
        self.ai_side: Side | None = None
        self.start_time = datetime.datetime.now()

    def is_move_valid(self, from_position: Position, to_position: Position) -> bool:
        from_piece = self.board.get_piece(from_position)
        to_piece = self.board.get_piece(to_position)

        # Moving an empty cell
        if from_piece is None:
            return False

        # Moving to a cell that is not empty
        if to_piece is not None:
            return False

        # Move to a neighbouring cell
        if to_position in from_piece.get_possible_moves(long_jump=False):
            return True

        # Move over an enemy piece
        if to_position in from_piece.get_possible_moves(long_jump=True):
            inbetween_piece = self.board.get_piece_between(from_position, to_position)
            if inbetween_piece is not None and inbetween_piece.side == from_piece.side.get_enemy():
                return True

        return False

    def get_valid_moves(self, piece: Piece) -> dict[Position, Move]:
        moves: dict[Position, Move] = dict()

        # Empty field
        if piece is None:
            return moves

        for position in piece.get_possible_moves(long_jump=False):
            if self.is_move_valid(piece.position, position):
                moves[position] = Move(piece, position, [])

        def long_jump(jumped_pieces: list[Piece]):
            # Go through valid double jumps
            for to_position in piece.get_possible_moves(long_jump=True):
                if not self.is_move_valid(piece.position, to_position):
                    continue

                # Add enemy piece to the list of jumped pieces
                # We know the piece between is an enemy because of the is_move_valid check
                enemy_piece = self.board.get_piece_between(piece.position, to_position)
                if enemy_piece in jumped_pieces:
                    continue
                moves[to_position] = Move(piece, to_position, jumped_pieces + [enemy_piece])

                # Temporarily move the piece to the new position
                original_position = piece.position
                self.board.update_piece_position(piece, to_position)

                # Check for more jumps with the new position
                long_jump(jumped_pieces + [enemy_piece])

                # Revert the temporary move
                self.board.update_piece_position(piece, original_position)

        long_jump([])

        return moves

    def apply_move(self, move: Move) -> None:
        self.board.update_piece_position(move.from_piece, move.to_position)

        # Remove jumped pieces
        for piece in move.jumped_pieces:
            self.board.delete_piece(piece)

        # Check if the piece should be crowned
        if move.from_piece.side == Side.WHITE and move.from_piece.position.row == 0:
            move.from_piece.is_king = True
        elif move.from_piece.side == Side.BLACK and move.from_piece.position.row == BOARD_SIZE - 1:
            move.from_piece.is_king = True

        self.next_move()

    def next_move(self) -> None:
        self.side_to_move = self.side_to_move.get_enemy()

    def get_all_valid_moves(self, side: Side) -> list[Move]:
        result: list[Move] = []

        pieces = self.board.get_pieces(side)
        for piece in pieces:
            moves = self.get_valid_moves(piece)
            result += moves.values()

        return result

    def get_best_move(self, moves: list[Move]) -> Move | None:
        # Piece jumps over an enemy piece
        JUMP_SCORE = 1.0
        # Piece becomes a king
        KING_SCORE = 0.75
        # Piece is currently threatened
        PROTECTION_SCORE = 0.5
        # Peace is threatened after the move (suicide protection (:)
        THREAT_AFTER_MOVE_SCORE = -0.75

        def threatened_by(piece: Piece) -> list[Piece]:
            """
            :return: list of pieces that can jump over the given piece
            """
            result: list[Piece] = []

            enemy_moves = self.get_all_valid_moves(piece.side.get_enemy())
            for enemy_move in enemy_moves:
                if piece in enemy_move.jumped_pieces:
                    result.append(enemy_move.from_piece)

            return result

        if not moves:
            return None

        # Score moves
        scores: dict[Move, float] = {}
        for move in moves:
            score: float = 0
            score += len(move.jumped_pieces) * JUMP_SCORE
            score += len(threatened_by(move.from_piece)) * PROTECTION_SCORE
            score += int(move.becomes_king()) * KING_SCORE

            # Temporarily make move and check if piece is threatened after
            original_position = move.from_piece.position
            self.board.update_piece_position(move.from_piece, move.to_position)
            score += len(threatened_by(move.from_piece)) * THREAT_AFTER_MOVE_SCORE

            # Revert the temporary move
            self.board.update_piece_position(move.from_piece, original_position)

            scores[move] = score

        best_score = max(scores.values())
        best_move = max(scores, key=scores.get)
        if best_score > 0:
            return best_move

        # No good move, move a regular piece to go towards becoming a king
        # Sort first by score, then by distance from edge
        sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], x[0].from_piece.distance_from_edge()))
        for move, score in sorted_scores:
            if not move.from_piece.is_king:
                return move

        # Everyone's a king, just move a random piece
        return random.choice(moves)

    def get_winner(self) -> Side | None:
        if not self.board.get_pieces(Side.WHITE):
            return Side.BLACK

        if not self.board.get_pieces(Side.BLACK):
            return Side.WHITE

        if not self.get_all_valid_moves(Side.WHITE):
            return Side.BLACK

        if not self.get_all_valid_moves(Side.BLACK):
            return Side.WHITE

        return None

    def get_game_time_seconds(self) -> int:
        return (datetime.datetime.now() - self.start_time).seconds

    def load_save_state(self, save):
        self.board = save.board
        self.side_to_move = save.current_turn
        self.ai_side = save.ai_side
        self.start_time = datetime.datetime.now() - datetime.timedelta(seconds=save.game_time_seconds)

    def is_ai_turn(self) -> bool:
        return self.side_to_move == self.ai_side

    def make_move(self, position: Position) -> None:
        moves = self.get_valid_moves(self.board.selected)
        self.board.selected = None

        # No valid moves => opponent wins
        if len(moves) == 0:
            return

        # Check if selected piece can move to the clicked field
        if position not in moves:
            return

        # Move the piece
        self.apply_move(moves[position])

    def select_piece(self, position: Position) -> list[Position]:
        """
        :param position: which piece to select
        :return: list of possible moves for the selected piece
        """
        piece = self.board.get_piece(position)

        # Empty field
        if piece is None:
            return []

        # Opponent's piece
        if piece.side != self.side_to_move:
            return []

        self.board.selected = piece

        moves = self.get_valid_moves(piece)
        return [move.to_position for move in moves.values()]

    def make_best_move(self):
        moves = self.get_all_valid_moves(self.side_to_move)
        move = self.get_best_move(moves)
        self.apply_move(move)
