from __future__ import annotations

from src.model.constants import BOARD_SIZE
from src.model.dataclasses import Position, Piece, Side


class Board:

    def __init__(self):
        self._board: dict[Position, Piece | None] = {}
        self.selected: Piece | None = None

    def set_initial_positions(self):
        ONE_SIDE_ROWS = 3

        # Place black pieces
        for row in range(ONE_SIDE_ROWS):
            for column in range(BOARD_SIZE):
                if (row + column) % 2 == 1:
                    position = Position(row, column)
                    self._board[position] = Piece(Side.BLACK, position)

        # Place white pieces
        for row in range(BOARD_SIZE - ONE_SIDE_ROWS, BOARD_SIZE):
            for column in range(BOARD_SIZE):
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
        if position.row < 0 or position.row >= BOARD_SIZE or position.column < 0 or position.column >= BOARD_SIZE:
            return None

        # Empty field
        if position not in self._board:
            return None

        return self._board[position]

    def get_piece_between(self, position1: Position, position2: Position) -> Piece | None:
        row = (position1.row + position2.row) // 2
        column = (position1.column + position2.column) // 2

        return self.get_piece(Position(row, column))

    def get_pieces(self, side: Side) -> list[Piece]:
        return [piece for piece in self._board.values() if piece.side == side]
