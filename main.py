from controller import Controller
from model import Checkers
from view import TkView

if __name__ == '__main__':
    controller = Controller(Checkers(), TkView())
    controller.start()
