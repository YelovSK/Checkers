from dataclasses import dataclass


@dataclass
class Position:
    row: int
    column: int

    def __hash__(self):
        return hash((self.row, self.column))

    def __str__(self):
        return f"{self.row}{self.column}"
