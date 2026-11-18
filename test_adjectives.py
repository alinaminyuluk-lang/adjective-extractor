import unittest
from pathlib import Path
from adjectives import extract_adjectives, TextValidationError


class TestAdjectiveExtractor(unittest.TestCase):
    def test_basic_sentence(self):
        text = "Сонячний теплий день подарував гарний настрій."
        res = extract_adjectives(text)
        words = [item["word"] for item in res["adjectives"]]
        self.assertEqual(words, ["Сонячний", "теплий", "гарний"])
        self.assertEqual(res["adj_count"], 3)

    def test_no_adjectives(self):
        text = "Студент програмує алгоритм."
        res = extract_adjectives(text)
        self.assertEqual(res["adj_count"], 0)
        self.assertEqual(res["percentage"], 0.0)

    def test_empty_input_raises_error(self):
        with self.assertRaises(TextValidationError):
            extract_adjectives("   ")

    def test_non_ukrainian_input_raises_error(self):
        with self.assertRaises(TextValidationError):
            extract_adjectives("12345 !!! Hello world")

    def test_sample_files_if_exist(self):
        for fname in ["test_1.txt", "test_2.txt", "test_3.txt"]:
            path = Path("data") / fname
            if path.exists():
                content = path.read_text(encoding="utf-8")
                res = extract_adjectives(content)
                self.assertGreater(res["adj_count"], 0)


if __name__ == "__main__":
    unittest.main()
