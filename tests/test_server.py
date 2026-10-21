
import unittest

from server import explain_error


class TestExplainError(unittest.TestCase):

    def test_key_error(self):
        result = explain_error("KeyError: username")
        self.assertIn("dictionary key", result)
        self.assertIn("dict.get()", result)

    def test_zero_division_error(self):
        result = explain_error("ZeroDivisionError")
        self.assertIn("divide by zero", result)

    def test_syntax_error(self):
        result = explain_error("SyntaxError")
        self.assertIn("syntax rules", result)

    def test_array_index_error(self):
        result = explain_error("ArrayIndexOutOfBoundsException")
        self.assertIn("array position", result)

    def test_empty_error_message(self):
        result = explain_error("")
        self.assertIn("Please enter an error message", result)

    def test_unknown_error(self):
        result = explain_error("SomeUnrecognizedProblem")
        self.assertIn("could not identify", result)


if __name__ == "__main__":
    unittest.main()