import sys

from src.Controller import Controller
from src.Game import Game
from src.View import TkView


def get_ai_opponent_arg():
    if len(sys.argv) > 1:
        return sys.argv[1] == "ai"

    return False


if __name__ == '__main__':
    controller = Controller(Game(), TkView(), ai_opponent=get_ai_opponent_arg())
    controller.start()
