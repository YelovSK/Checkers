from model import Checkers, Position, PieceType
from view import TkView


class Controller:

    def __init__(self, checkers: Checkers, view: TkView):
        self.checkers = checkers
        self.view = view

    def start(self):
        self.view.setup(self)
        self.view.draw_board()
        self.view.draw_pieces(self.checkers.board)
        self.view.start_main_loop()

    def handle_click(self, position: Position):
        self.view.clear_highlights()

        piece = self.checkers.board.get_piece(position)
        if piece is None:
            return

        if piece.piece_type == PieceType.EMPTY:
            return

        piece.select()
        moves = self.checkers.get_valid_moves(position)
        self.view.highlight_fields(list(moves.keys()))
        self.view.highlight_piece(position)
        print(position)
        print("pojebal som ti mamku kokotko")
