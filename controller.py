from model import Checkers, Position
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
        #### TMP
        # moves = self.checkers.get_all_valid_moves(self.checkers.side_to_move)
        # move = self.checkers.get_best_move(moves)
        # self.checkers.apply_move(move)
        # self.view.draw_pieces(self.checkers.board)
        # return
        #### TMP

        self.view.clear_highlights()

        piece = self.checkers.board.get_piece(click_position)

        # No piece is selected => select the clicked piece
        if self.checkers.board.selected is None:
            # Clicked on an empty field
            if piece is None:
                return

            # Clicked on an opponent's piece
            if piece.side != self.checkers.side_to_move:
                return

            self.checkers.board.selected = piece

            # Highlight valid moves
            moves = self.checkers.get_valid_moves(piece)
            self.view.highlight_fields([move.to_position for move in moves.values()])
            self.view.highlight_piece(click_position)
            return

        moves = self.checkers.get_valid_moves(self.checkers.board.selected)
        self.checkers.board.selected = None

        # Check if selected piece can move to the clicked field
        if click_position not in moves:
            return

        # Move the piece
        self.checkers.apply_move(moves[click_position])

        # Redraw the pieces
        self.view.draw_pieces(self.checkers.board)
