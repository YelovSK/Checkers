from model import Checkers, Position, Side
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

    def handle_click(self, click_position: Position):
        self.view.clear_highlights()

        # Should not be possible to click outside of the board, but just in case
        try:
            piece = self.checkers.board.get_piece(click_position)
        except IndexError:
            return

        if not self.checkers.board.selected:
            if piece is None:
                return

            self.checkers.board.selected = piece
            # moves = self.checkers.get_valid_moves(click_position)
            # self.view.highlight_fields(list(moves.keys()))
            # self.view.highlight_piece(click_position)

            moves = self.checkers.get_valid_moves(piece)
            self.view.highlight_fields([move.to_position for move in moves.values()])
            self.view.highlight_piece(click_position)
            return

        moves = self.checkers.get_valid_moves(self.checkers.board.selected)

        # Check if move is valid
        if click_position not in moves:
            self.checkers.board.selected = None
            return

        # Move the piece
        self.checkers.apply_move(moves[click_position])
        self.checkers.board.selected = None

        # Redraw the pieces
        self.view.draw_pieces(self.checkers.board)

        # TODO:
        # - Empty should be done differently idfk shit's ugly
        # - the get_moves() is fucking broken
        # - actually everything is broken gg
