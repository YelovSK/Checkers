from __future__ import annotations

from src.Game import Game
from src.View import TkView
from src.model.SaveParser import SaveParser, SaveResult
from src.model.dataclasses import Position


class Controller:
    def __init__(self, checkers: Game, view: TkView, ai_opponent: bool):
        self.game = checkers
        self.view = view
        self.is_ai_opponent = ai_opponent
        SaveParser.create_saves_folder()

    def start(self):
        self.view.setup(self)
        self.view.draw_board()
        if self.is_ai_opponent:
            self._choose_side()

        self.view.draw_pieces(self.game.board)
        self.view.start_main_loop()

    def save(self):
        file_path = self.view.open_save_dialog(SaveParser.SAVES_FOLDER)
        if file_path is None:
            return

        try:
            SaveParser.save(self.game.board,
                            self.game.side_to_move,
                            self.game.ai_side,
                            self.game.get_game_time_seconds(),
                            file_path)
        except Exception as e:
            self.view.show_error(repr(e))

    def load(self):
        file_name = self.view.open_load_dialog(SaveParser.SAVES_FOLDER)
        if file_name == "":
            return

        try:
            save: SaveResult = SaveParser.load(file_name)
        except FileNotFoundError:
            self.view.show_error("File not found")
            return
        except:
            self.view.show_error("Invalid save file (.. or bug)")
            return

        self.game.load_save_state(save)
        self.is_ai_opponent = self.game.ai_side is not None

        self.view.clear_highlights()
        self.view.draw_pieces(self.game.board)

    def restart(self):
        self.game = Game()
        if self.is_ai_opponent:
            self._choose_side()

        self.view.clear_highlights()
        self.view.draw_pieces(self.game.board)

    def handle_click(self, click_position: Position):
        self.view.clear_highlights()

        self._make_user_move(click_position)

        winner_side = self.game.get_winner()
        if winner_side is not None:
            self.view.show_winner(winner_side, self.game.get_game_time_seconds())

    # region Private methods

    def _choose_side(self):
        self.game.ai_side = self.view.open_choose_side_window().get_enemy()
        if self.game.ai_side.is_first_to_move():
            self._make_ai_move_delayed()

    def _make_ai_move_delayed(self):
        DELAY_MS = 500
        self.view._canvas.after(DELAY_MS, self._make_ai_move)

    def _make_user_move(self, click_position: Position):
        if self.game.is_ai_turn():
            return

        # No piece is selected => select the clicked piece
        if self.game.board.selected is None:
            valid_moves = self.game.select_piece(click_position)
            if len(valid_moves) > 0:
                self.view.highlight_fields(valid_moves)
                self.view.highlight_piece(click_position)
        # Some piece is selected => try to move it to the clicked position
        else:
            self.game.make_move(click_position)
            self.view.draw_pieces(self.game.board)

            # AI's turn
            self._make_ai_move_delayed()

    def _make_ai_move(self):
        if not self.game.is_ai_turn():
            return

        self.game.make_best_move()
        self.view.draw_pieces(self.game.board)

    # endregion Private methods
