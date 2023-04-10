from dataclasses import dataclass

from src.model.constants import BOARD_SIZE
from src.model.dataclasses import Position
from src.model.dataclasses.Side import Side


@dataclass
class Piece:
    side: Side
    position: Position
    is_king: bool = False

    WHITE = "w"
    BLACK = "b"
    WHITE_KING = "W"
    BLACK_KING = "B"

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
            if 0 <= position.row < BOARD_SIZE and 0 <= position.column < BOARD_SIZE:
                result.append(position)

        return result

    def distance_from_edge(self) -> int:
        if self.side == Side.WHITE:
            return self.position.row
        elif self.side == Side.BLACK:
            return BOARD_SIZE - self.position.row - 1
        raise ValueError("Unknown side")

    @staticmethod
    def get_from_string(string: str) -> "Piece":
        side = Side.WHITE if string[0] == Piece.WHITE or string[0] == Piece.WHITE_KING else Side.BLACK
        is_king = string[0] == Piece.WHITE_KING or string[0] == Piece.BLACK_KING
        position = Position(int(string[1]), int(string[2]))
        return Piece(side, position, is_king)

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        result = ""

        if self.is_king:
            if self.side == Side.WHITE:
                result += self.WHITE_KING
            elif self.side == Side.BLACK:
                result += self.BLACK_KING
        else:
            if self.side == Side.WHITE:
                result += self.WHITE
            elif self.side == Side.BLACK:
                result += self.BLACK

        result += str(self.position)
        return result
