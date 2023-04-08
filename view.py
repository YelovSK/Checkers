from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

from model import Board, Position, Side, Piece


@dataclass
class Coords:
    x: int
    y: int


class TkView:
    WINDOWS_SIZE = 500
    FIELD_SIZE = WINDOWS_SIZE / Board.SIZE
    PIECE_SIZE = FIELD_SIZE * 0.8

    LIGHT_FIELD_COLOR = "#ffceaf"
    DARK_FIELD_COLOR = "#a34911"
    BACKGROUND_COLOR = "#bcbcbc"

    LIGHT_PIECE_COLOR = "#ffffff"
    DARK_PIECE_COLOR = "#000000"

    def __init__(self):
        self._root = None
        self._canvas = None
        # Canvas objects
        self._highlights_graphics: list[int] = []
        self._pieces_graphics: list[int] = []

    def setup(self, controller) -> None:
        # Root
        self._root = tk.Tk()
        self._root.title("Checkers")
        self._root.iconbitmap("icon.ico")
        self._root.resizable(False, False)

        # Canvas
        self._canvas = tk.Canvas(self._root, width=self.WINDOWS_SIZE, height=self.WINDOWS_SIZE,
                                 bg=self.BACKGROUND_COLOR)
        self._canvas.bind_all("<ButtonPress-1>",
                              lambda event: controller.handle_click(self._get_field_position(Coords(event.x, event.y))))

        # Menu
        # menu = tk.Menu(self.root)
        # self.root.config(menu=menu)
        # sub_menu = tk.Menu(menu, tearoff=0)
        # menu.add_cascade(label="File", menu=sub_menu)
        # Q: Why does it say controller.save is unresolved?
        # A: Because you are importing the module, not the class.
        # Q: No, I am importing the class.
        # A: No, you are importing the module.
        # Q: No, I am importing the class.
        # A: No, you are importing the module.
        # Q: No, I am importing the class.
        # A: No, you are importing the module.
        # sub_menu.add_command(label="Save", command=controller.save)
        # sub_menu.add_command(label="Load", command=controller.load)
        # sub_menu.add_command(label="Restart", command=controller.restart)
        # sub_menu.add_command(label="Exit", command=exit)

    def draw_board(self) -> None:
        self._canvas.delete("all")
        for row in range(Board.SIZE):
            for col in range(Board.SIZE):
                color = self._get_field_color(Position(row, col))
                canvas_coords = self._get_field_coords(Position(row, col))

                self._canvas.create_rectangle(canvas_coords.x, canvas_coords.y,
                                              canvas_coords.x + self.FIELD_SIZE,
                                              canvas_coords.y + self.FIELD_SIZE,
                                              fill=color, outline="")

        self._canvas.update()

    def draw_pieces(self, board: Board) -> None:
        self._clear_pieces_graphics()

        for row in range(Board.SIZE):
            for col in range(Board.SIZE):
                piece = board.get_piece(Position(row, col))
                self._draw_piece(piece, Position(row, col))

        self._canvas.update()

    def start_main_loop(self):
        self._canvas.pack()
        self._root.mainloop()

    # region Private methods

    def clear_highlights(self) -> None:
        for highlight in self._highlights_graphics:
            self._canvas.delete(highlight)

        self._highlights_graphics.clear()

    def _clear_pieces_graphics(self) -> None:
        for piece in self._pieces_graphics:
            self._canvas.delete(piece)

        self._pieces_graphics.clear()

    def _draw_piece(self, piece: Piece, coords: Position) -> None:
        if piece is None:
            return

        # Draw circle
        color = self._get_piece_color(piece)
        canvas_coords = self._get_field_coords(coords)
        offset = (self.FIELD_SIZE - self.PIECE_SIZE) / 2

        oval = self._canvas.create_oval(canvas_coords.x + offset, canvas_coords.y + offset,
                                        canvas_coords.x + self.PIECE_SIZE + offset,
                                        canvas_coords.y + self.PIECE_SIZE + offset,
                                        fill=color, outline="")
        self._pieces_graphics.append(oval)

        # Draw crown
        if not piece.is_king:
            return

        crown = self._canvas.create_text(canvas_coords.x + self.FIELD_SIZE / 2,
                                         canvas_coords.y + self.FIELD_SIZE / 2,
                                         text="♔",
                                         fill=self.DARK_PIECE_COLOR if piece.side == Side.WHITE else self.LIGHT_PIECE_COLOR,
                                         font="helvetica 30")
        self._pieces_graphics.append(crown)

    def _get_field_coords(self, position: Position) -> Coords:
        return Coords(position.column * self.FIELD_SIZE, position.row * self.FIELD_SIZE)

    def _get_piece_color(self, piece: Piece) -> str | None:
        if piece is None:
            return None

        return self.LIGHT_PIECE_COLOR if piece.side == Side.WHITE else self.DARK_PIECE_COLOR

    def _get_field_color(self, position: Position) -> str:
        return self.LIGHT_FIELD_COLOR if (position.row + position.column) % 2 == 0 else self.DARK_FIELD_COLOR

    def _get_field_position(self, coords: Coords) -> Position:
        return Position(int(coords.y // self.FIELD_SIZE), int(coords.x // self.FIELD_SIZE))

    # endregion Private methods
    def highlight_fields(self, positions: list[Position]) -> None:
        for position in positions:
            canvas_coords = self._get_field_coords(position)

            rectangle = self._canvas.create_rectangle(canvas_coords.x, canvas_coords.y,
                                                      canvas_coords.x + self.FIELD_SIZE,
                                                      canvas_coords.y + self.FIELD_SIZE,
                                                      fill="", outline="red", width=3)
            self._highlights_graphics.append(rectangle)

    def highlight_piece(self, position: Position) -> None:
        canvas_coords = self._get_field_coords(position)
        offset = (self.FIELD_SIZE - self.PIECE_SIZE) / 2

        oval = self._canvas.create_oval(canvas_coords.x + offset, canvas_coords.y + offset,
                                        canvas_coords.x + self.PIECE_SIZE + offset,
                                        canvas_coords.y + self.PIECE_SIZE + offset,
                                        fill="", outline="red", width=2)
        self._highlights_graphics.append(oval)
