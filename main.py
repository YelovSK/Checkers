import sys

from src.controller import GameController
from src.model import Game
from src.view import MainWindow


def get_ai_opponent_arg():
    if len(sys.argv) > 1:
        return sys.argv[1] == "ai"

    return False


if __name__ == '__main__':
    controller = GameController(Game(), MainWindow(), ai_opponent=get_ai_opponent_arg())
    controller.start()
