from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class Side(Enum):
    WHITE = 1
    BLACK = 2

    def get_enemy(self) -> Side:
        if self == Side.WHITE:
            return Side.BLACK
        elif self == Side.BLACK:
            return Side.WHITE
        raise ValueError("Unknown side")


@dataclass
class Piece:
    side: Side
    position: Position
    is_king: bool = False

    def get_possible_moves(self, long_jump: bool = False) -> list[Position]:
        """
        :return: list of all positions 1 or 2 fields away from the piece
        """
        result: list[Position] = []
        jump_length = 2 if long_jump else 1

        directions: tuple[tuple[int, int], ...] = ()
        if self.is_king:
            directions = ((jump_length, jump_length),
                          (jump_length, -jump_length),
                          (-jump_length, jump_length),
                          (-jump_length, -jump_length))
        elif self.side == Side.WHITE:
            directions = ((-jump_length, jump_length),
                          (-jump_length, -jump_length))
        elif self.side == Side.BLACK:
            directions = ((jump_length, jump_length),
                          (jump_length, -jump_length))

        for row, column in directions:
            position = Position(self.position.row + row, self.position.column + column)
            if 0 <= position.row < Board.SIZE and 0 <= position.column < Board.SIZE:
                result.append(position)

        return result

    def distance_from_edge(self) -> int:
        if self.side == Side.WHITE:
            return self.position.row
        elif self.side == Side.BLACK:
            return Board.SIZE - self.position.row - 1
        raise ValueError("Unknown side")

    def __hash__(self):
        return hash(self.position)


@dataclass
class Position:
    row: int
    column: int

    def __hash__(self):
        return hash((self.row, self.column))


@dataclass
class Move:
    from_piece: Piece
    to_position: Position
    jumped_pieces: list[Piece] = None

    def becomes_king(self) -> bool:
        return (self.from_piece.side == Side.WHITE and self.to_position.row == 0) or \
            (self.from_piece.side == Side.BLACK and self.to_position.row == Board.SIZE - 1)

    def __hash__(self):
        return hash((self.from_piece, self.to_position))


class Board:
    SIZE = 8
    ONE_SIDE_ROWS = 3

    def __init__(self):
        self._board: dict[Position, Piece | None] = {}
        self.selected: Piece | None = None

        # Place black pieces
        for row in range(self.ONE_SIDE_ROWS):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    position = Position(row, column)
                    self._board[position] = Piece(Side.BLACK, position)

        # Place white pieces
        for row in range(self.SIZE - self.ONE_SIDE_ROWS, self.SIZE):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    position = Position(row, column)
                    self._board[position] = Piece(Side.WHITE, position)

    def delete_piece(self, piece: Piece) -> None:
        if piece.position in self._board:
            del self._board[piece.position]

    def set_piece(self, piece: Piece) -> None:
        self._board[piece.position] = piece

    def update_piece_position(self, piece: Piece, position: Position) -> None:
        self.delete_piece(piece)
        piece.position = position
        self.set_piece(piece)

    def get_piece(self, position: Position) -> Piece | None:
        # Check if the position is on the board
        if position.row < 0 or position.row >= self.SIZE or position.column < 0 or position.column >= self.SIZE:
            return None

        # None means that the field is empty
        if position not in self._board:
            return None

        return self._board[position]

    def get_piece_between(self, position1: Position, position2: Position) -> Piece | None:
        row = (position1.row + position2.row) // 2
        column = (position1.column + position2.column) // 2

        return self.get_piece(Position(row, column))

    def get_pieces(self, side: Side) -> list[Piece]:
        return [piece for piece in self._board.values() if piece.side == side]


class Checkers:

    def __init__(self):
        self.board = Board()
        self.side_to_move = Side.BLACK

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
        elif move.from_piece.side == Side.BLACK and move.from_piece.position.row == Board.SIZE - 1:
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

        return None
