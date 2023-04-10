from __future__ import annotations

import random
import tkinter as tk

from src.model.dataclasses import Side
from src.view import MainWindow


class SideWindow(tk.Toplevel):

    def __init__(self):
        super().__init__()
        self.result: Side | None = None
        self._setup()

    def wait_for_result(self) -> Side:
        self.wait_window()
        return self.result

    def _setup(self):
        self.title("Choose side")
        self.iconbitmap(MainWindow.ICON_FILE)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.geometry("260x110")
        self.protocol("WM_DELETE_self", lambda: self.destroy())

        label = tk.Label(self, text="Choose side", font=("Helvetica", 15))
        label.pack()

        button_properties = {
            "font": ("helvetica", 13),
            "bd": 2,
            "master": self,
        }

        black_button = tk.Button(
            **button_properties,
            text="BLACK",
            background="black",
            fg="white",
            activeforeground="#ffffff",
            activebackground="#444444",
            command=lambda: self._button_clicked(Side.BLACK)
        )

        white_button = tk.Button(
            **button_properties,
            text="WHITE",
            background="white",
            command=lambda: self._button_clicked(Side.WHITE)
        )

        random_button = tk.Button(
            **button_properties,
            text="RANDOM",
            background="gray",
            command=lambda: self._button_clicked(random.choice([Side.BLACK, Side.WHITE]))
        )

        black_button.place(x=10, y=50)
        white_button.place(x=90, y=50)
        random_button.place(x=165, y=50)

    def _button_clicked(self, side: Side):
        self.result = side
        self.destroy()
