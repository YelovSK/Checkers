from model import Checkers, Position, Side
from view import TkView


class Controller:
    def __init__(self, checkers: Checkers, view: TkView):
        self.checkers = checkers
        self.view = view
        self.AI_side = Side.WHITE

    def start(self):
        self.view.setup(self)
        self.view.draw_board()
        self.view.start_main_loop()

    def handle_click(self, click_position: Position):
        self.view.clear_highlights()

        moved_piece = self.make_user_move(click_position)

        if moved_piece:
            self.view._canvas.after(500, self.make_AI_move)

        winner_side = self.checkers.get_winner()
        if winner_side is not None:
            self.view.show_winner(winner_side)

    def make_user_move(self, click_position: Position) -> bool:
        if self.checkers.side_to_move == self.AI_side:
            return False

        piece = self.checkers.board.get_piece(click_position)

        # No piece is selected => select the clicked piece
        if self.checkers.board.selected is None:
            # Clicked on an empty field
            if piece is None:
                return False

            # Clicked on an opponent's piece
            if piece.side != self.checkers.side_to_move:
                return False

            self.checkers.board.selected = piece

            # Highlight valid moves
            moves = self.checkers.get_valid_moves(piece)
            self.view.highlight_fields([move.to_position for move in moves.values()])
            self.view.highlight_piece(piece.position)
            return False

        moves = self.checkers.get_valid_moves(self.checkers.board.selected)
        self.checkers.board.selected = None

        # No valid moves => opponent wins
        if len(moves) == 0:
            return False

        # Check if selected piece can move to the clicked field
        if click_position not in moves:
            return False

        # Move the piece
        self.checkers.apply_move(moves[click_position])
        self.view.draw_pieces(self.checkers.board)

        return True

    def make_AI_move(self) -> bool:
        moves = self.checkers.get_all_valid_moves(self.AI_side)

        # No valid moves => opponent wins
        if len(moves) == 0:
            self.view.show_winner(self.AI_side.get_enemy())
            return False

        move = self.checkers.get_best_move(moves)
        self.checkers.apply_move(move)
        self.view.draw_pieces(self.checkers.board)

        # User has no valid moves => AI wins
        if len(self.checkers.get_all_valid_moves(self.AI_side.get_enemy())) == 0:
            self.view.show_winner(self.AI_side)

        return True
