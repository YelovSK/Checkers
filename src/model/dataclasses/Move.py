from dataclasses import dataclass

from src.model.Constants import BOARD_SIZE
from src.model.dataclasses import Piece, Position, Side


@dataclass
class Move:
    from_piece: Piece
    to_position: Position
    jumped_pieces: list[Piece] = None

    def becomes_king(self) -> bool:
        return (self.from_piece.side == Side.WHITE and self.to_position.row == 0) or \
            (self.from_piece.side == Side.BLACK and self.to_position.row == BOARD_SIZE - 1)

    def __hash__(self):
        return hash((self.from_piece, self.to_position))
