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

    def handle_click(self, position: Position):
        print(position)
        print("pojebal som ti mamku kokotko")
        pass
