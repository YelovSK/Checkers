from src.Controller import Controller
from src.Game import Game
from src.View import TkView

if __name__ == '__main__':
    controller = Controller(Game(), TkView(), ai_opponent=True)
    controller.start()
