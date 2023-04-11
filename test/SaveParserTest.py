import unittest
import os
from src.model import SaveParser
from src.model.dataclasses import Side


class SaveParserTest(unittest.TestCase):
    def test_load(self):
        # assert with exception
        with self.assertRaises(FileNotFoundError):
            SaveParser.load("not_existing_file.txt")

    def test_load_no_exception(self):
        # assert without exception
        save_result = SaveParser.load("test_save.txt")
        assert save_result.board is not None
        assert save_result.current_turn == Side.BLACK
        assert save_result.ai_side is None
        assert save_result.game_time_seconds == 18

    def test_save(self):
        save_result1 = SaveParser.load("test_save.txt")
        SaveParser.save(save_result1.board, save_result1.current_turn, save_result1.ai_side, save_result1.game_time_seconds, "test_save2.txt")
        save_result2 = SaveParser.load("test_save2.txt")
        # remove file after test
        os.remove("test_save2.txt")
        assert save_result1.board._board == save_result2.board._board
        assert save_result1.current_turn == save_result2.current_turn
        assert save_result1.ai_side == save_result2.ai_side
        assert save_result1.game_time_seconds == save_result2.game_time_seconds



if __name__ == '__main__':
    unittest.main()
