import os
from dataclasses import dataclass

from src.model.Board import Board
from src.model.dataclasses import Side, Piece


@dataclass
class SaveResult:
    board: Board
    current_turn: Side
    ai_side: Side
    game_time_seconds: int


class SaveParser:
    SAVES_FOLDER = "save"

    WHITE = "w"
    BLACK = "b"
    WHITE_KING = "W"
    BLACK_KING = "B"

    @staticmethod
    def create_saves_folder():
        if not os.path.exists(SaveParser.SAVES_FOLDER):
            os.mkdir(SaveParser.SAVES_FOLDER)

    @staticmethod
    def load(file_path: str) -> SaveResult:
        board = Board()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        with open(file_path) as f:
            current_turn = getattr(Side, f.readline().strip())
            ai_side = getattr(Side, f.readline().strip())
            game_time_seconds = int(f.readline().strip())
            pieces_str = f.readline().strip().split(" ")
            for piece_str in pieces_str:
                board.set_piece(Piece.get_from_string(piece_str))

        return SaveResult(board, current_turn, ai_side, game_time_seconds)

    @staticmethod
    def save(board: Board, current_turn: Side, ai_side: Side, game_time_seconds: int, file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write(current_turn.name + "\n")
            if ai_side is None:
                f.write("\n")
            else:
                f.write(ai_side.name + "\n")
            f.write(str(game_time_seconds) + "\n")
            pieces = board.get_pieces(Side.BLACK) + board.get_pieces(Side.WHITE)
            f.write(" ".join([str(piece) for piece in pieces]))
