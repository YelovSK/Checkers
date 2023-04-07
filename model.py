from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InvalidBoardCell(Exception):
    pass


class PieceType(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2


class EmptyPiece:

    def __init__(self):
        self.piece_type = PieceType.EMPTY

    def get_possible_moves(self, jump_length=1) -> list[Position]:
        return []


class Piece(EmptyPiece):
    def __init__(self, piece_type: PieceType, row: int, column: int, king: bool = False):
        self.piece_type = piece_type
        self.king = king
        self.row = row
        self.column = column

    def get_possible_moves(self, jump_length=1) -> list[Position]:
        """
        :return: list of all positions 1 or 2 fields away from the piece
        """
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

        for column in (-1, 1):
            for row in directions:
                x = self.row + row
                y = self.column + column
                if 0 <= x < Board.SIZE and 0 <= y < Board.SIZE:
                    result.append(Position(x, y))

        return result

    def get_enemy_type(self) -> PieceType:
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

    def __hash__(self):
        return hash((self.row, self.column))


@dataclass
class Move:
    from_position: Position
    to_position: Position
    jumped_positions: list[Position] = None


class Board:
    SIZE = 8
    ONE_SIDE_ROWS = 3

    def __init__(self):
        self._board = [[EmptyPiece() for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.selected: Position | None = None

        # Place black pieces
        for row in range(self.ONE_SIDE_ROWS):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    self._board[row][column] = Piece(PieceType.BLACK, row, column)

        # Place white pieces
        for row in range(self.SIZE - self.ONE_SIDE_ROWS, self.SIZE):
            for column in range(self.SIZE):
                if (row + column) % 2 == 1:
                    self._board[row][column] = Piece(PieceType.WHITE, row, column)

    def delete_piece(self, position: Position) -> None:
        self._board[position.row][position.column] = EmptyPiece()

    def set_piece(self, position: Position, piece: Piece) -> None:
        try:
            self._board[position.row][position.column] = piece
        except IndexError:
            raise InvalidBoardCell()

    def get_piece(self, position: Position) -> Piece:
        try:
            return self._board[position.row][position.column]
        except IndexError:
            return None

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
        from_piece = self.board.get_piece(from_position)
        to_piece = self.board.get_piece(to_position)

        if from_piece is None or to_piece is None:
            return False

        # Moving an empty cell
        if from_piece.piece_type == PieceType.EMPTY:
            return False

        # Moving to a cell that is not empty
        if to_piece.piece_type != PieceType.EMPTY:
            return False

        # Move to an empty neighbouring cell
        for position in from_piece.get_possible_moves(jump_length=1):
            if position != to_position:
                continue
            if self.board.get_piece(position).piece_type == PieceType.EMPTY:
                return True

        # Move over an enemy piece
        for position in from_piece.get_possible_moves(jump_length=2):
            if position != to_position:
                continue
            if self.board.get_piece(position).piece_type != PieceType.EMPTY:
                continue

            piece_between = self.board.get_piece_between(from_position, to_position)
            # The piece between is an enemy piece
            if piece_between.piece_type == from_piece.get_enemy_type():
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

        for position in piece.get_possible_moves(jump_length=1):
            to_position = Position(piece_position.row + position.row, piece_position.column + position.column)
            if self.is_move_valid(piece_position, to_position):
                moves[to_position] = []

        def long_jump(position: Position, prev=[]):  # rekurzivne najde tahy a vyhodene figurky 
            piece = self.board.get_piece(position)

            for move in piece.get_possible_moves(jump_length=2):
                to_position = Position(position.row + move.row, position.column + move.column)
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

    def get_valid_moves2(self, piece_position: Position) -> dict[Position, Move]:
        moves: dict[Position, Move] = dict()

        try:
            piece = self.board.get_piece(piece_position)
        except InvalidBoardCell:
            return moves

        for position in piece.get_possible_moves(jump_length=1):
            if self.is_move_valid(piece_position, position):
                moves[position] = Move(piece_position, position, [])

        def long_jump(position: Position, prev: list[Position] = []):  # rekurzivne najde tahy a vyhodene figurky 
            piece = self.board.get_piece(position)

            for move in piece.get_possible_moves(jump_length=2):
                to_position = Position(position.row + move.row, position.column + move.column)
                if not self.is_move_valid(position, to_position):
                    continue

                # x, y = move[0][0], move[0][1]
                # moves[move[0]] = [move[1]] + prev
                position_between = self.board.get_position_between(position, to_position)
                moves[to_position] = Move(piece_position, to_position, prev + [position_between])

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

    def apply_move(self, move: Move) -> None:
        # Add the piece to the new position
        self.board.set_piece(move.to_position, self.board.get_piece(move.from_position))
        # Delete the piece from the old position
        self.board.delete_piece(move.from_position)

        for position in move.jumped_positions:
            self.board.delete_piece(position)
