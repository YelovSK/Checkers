from enum import Enum


class Side(Enum):
    WHITE = 1
    BLACK = 2

    def get_enemy(self) -> "Side":
        if self == Side.WHITE:
            return Side.BLACK
        elif self == Side.BLACK:
            return Side.WHITE
        raise ValueError("Unknown side")

    def is_first_to_move(self) -> bool:
        return self == Side.BLACK
