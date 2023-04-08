from __future__ import annotations

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
        self._board[piece.position] = None

    def set_piece(self, piece: Piece) -> None:
        self._board[piece.position] = piece

    def update_piece_position(self, piece: Piece, position: Position) -> None:
        self.delete_piece(piece)
        piece.position = position
        self.set_piece(piece)

    def get_piece(self, position: Position) -> Piece | None:
        # Check if the position is on the board
        if position.row < 0 or position.row >= self.SIZE or position.column < 0 or position.column >= self.SIZE:
            raise IndexError()

        # None means that the field is empty
        if position not in self._board:
            return None

        return self._board[position]

    def get_piece_between(self, position1: Position, position2: Position) -> Piece | None:
        row = (position1.row + position2.row) // 2
        column = (position1.column + position2.column) // 2

        return self.get_piece(Position(row, column))


class Checkers:

    def __init__(self):
        self.board = Board()

    def is_move_valid(self, from_position: Position, to_position: Position) -> bool:
        try:
            from_piece = self.board.get_piece(from_position)
            to_piece = self.board.get_piece(to_position)
        except IndexError:
            return False

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
