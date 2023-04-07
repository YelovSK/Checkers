from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InvalidBoardCell(Exception):
    pass


class PieceType(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2


class Piece:
    def __init__(self, piece_type: PieceType, king: bool = False):
        self.piece_type = piece_type
        self.king = king

    def moves(self, jump_length=1) -> list[Position]:
        result: list[Position] = []
        if jump_length not in (1, 2):
            return result

        if self.king:
            directions = (jump_length, -jump_length)
        elif self.piece_type == PieceType.WHITE:
            directions = (-jump_length,)
        elif self.piece_type == PieceType.BLACK:
            directions = (jump_length,)
        else:
            return result

        for row in (-jump_length, jump_length):
            for column in directions:
                result.append(Position(row, column))

        return result

    def enemy_type(self) -> PieceType:
        if self.piece_type == PieceType.WHITE:
            return PieceType.BLACK
        elif self.piece_type == PieceType.BLACK:
            return PieceType.WHITE
        else:
            return PieceType.EMPTY


@dataclass
class Position:
    row: int
    column: int


class Board:
    SIZE = 8
    ONE_SIDE_ROWS = 3

    def __init__(self):
        self._board = [[Piece(PieceType.EMPTY) for _ in range(self.SIZE)] for _ in range(self.SIZE)]

        # Place black pieces
        for row in range(self.ONE_SIDE_ROWS):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    self._board[row][column] = Piece(PieceType.BLACK)

        # Place white pieces
        for row in range(self.SIZE - self.ONE_SIDE_ROWS, self.SIZE):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    self._board[row][column] = Piece(PieceType.WHITE)

    def delete_piece(self, position: Position) -> None:
        self._board[position.row][position.column] = Piece(PieceType.EMPTY)

    def set_piece(self, position: Position, piece: Piece) -> None:
        try:
            self._board[position.row][position.column] = piece
        except IndexError:
            raise InvalidBoardCell()

    def get_piece(self, position: Position) -> Piece:
        try:
            return self._board[position.row][position.column]
        except IndexError:
            raise InvalidBoardCell()

    def get_piece_between(self, position1: Position, position2: Position) -> Piece:
        try:
            position = self.get_position_between(position1, position2)
            return self._board[position.row][position.column]
        except IndexError:
            raise InvalidBoardCell()

    @staticmethod
    def get_position_between(position1: Position, position2: Position) -> Position:
        try:
            return Position((position1.row + position2.row) // 2, (position1.column + position2.column) // 2)
        except IndexError:
            raise InvalidBoardCell()


class Checkers:

    def __init__(self):
        self.board = Board()
        # self.checked: Piece = None

    def is_move_valid(self, from_position: Position, to_position: Position) -> bool:
        try:
            from_piece = self.board.get_piece(from_position)
            to_piece = self.board.get_piece(to_position)
        except IndexError:
            return False

        # Moving an empty cell
        if from_piece.piece_type == PieceType.EMPTY:
            return False

        # Moving to a cell that is not empty
        if to_piece.piece_type != PieceType.EMPTY:
            return False

        # Move to an empty neighbouring cell
        for position in from_piece.moves(jump_length=1):
            if self.board.get_piece(position).piece_type == PieceType.EMPTY:
                return True

        # Move over an enemy piece
        for position in from_piece.moves(jump_length=2):
            if self.board.get_piece(position).piece_type != PieceType.EMPTY:
                continue

            piece_between = self.board.get_piece_between(from_position, to_position)
            # The piece between is an enemy piece
            if piece_between.piece_type == from_piece.enemy_type():
                return True

        return False

    def get_valid_moves(self, piece_position: Position) -> dict[Position, list[Position]]:
        """
        :return: Dictionary where keys are target coordinates and values are coordinates
        of pieces that will be deleted if the move is made.
        """
        moves: dict[Position, list[Position]] = {}

        try:
            piece = self.board.get_piece(piece_position)
        except InvalidBoardCell:
            return moves

        for position in piece.moves(jump_length=1):
            to_position = Position(piece_position.row + position.row, piece_position.column + position.column)
            if self.is_move_valid(piece_position, to_position):
                moves[to_position] = []

        def long_jump(position: Position, prev=[]):  # rekurzivne najde tahy a vyhodene figurky 
            piece = self.board.get_piece(position)
            for x, y, in piece.moves(jump_length=2):
                to_position = Position(position.row + x, position.column + y)
                if not self.is_move_valid(position, to_position):
                    continue

                # x, y = move[0][0], move[0][1]
                # moves[move[0]] = [move[1]] + prev
                position_between = self.board.get_position_between(position, to_position)
                moves[to_position] = [position_between] + prev

                # pom = self.board[x][y] = Piece(field.side, (x, y), self.rect_size, field.king)
                temp = Piece(piece.piece_type, piece.king)
                self.board.set_piece(to_position, temp)

                # long_jump(pom, prev + [move[1]])
                long_jump(to_position, prev + [position_between])

                # del pom
                # self.board[x][y] = None
                del position_between
                self.board.delete_piece(to_position)

        long_jump(piece_position)

        return moves
