import unittest
from server import explain_error


class TestExplainError(unittest.TestCase):

    def test_key_error(self):
        result = explain_error("KeyError: 'username'")
        self.assertIn("keyerror", result.lower())
        self.assertIn("Explanation and fix", result)

    def test_zero_division_error(self):
        result = explain_error("ZeroDivisionError: division by zero")
        self.assertIn("zerodivisionerror", result.lower())
        self.assertIn("Explanation and fix", result)

    def test_syntax_error(self):
        result = explain_error("SyntaxError: invalid syntax")
        self.assertIn("syntaxerror", result.lower())
        self.assertIn("Explanation and fix", result)

    def test_array_index_error(self):
        result = explain_error(
            "ArrayIndexOutOfBoundsException: Index 5 out of bounds"
        )
        self.assertIn("arrayindexoutofboundsexception", result.lower())
        self.assertIn("Explanation and fix", result)

    def test_empty_error_message(self):
        result = explain_error("")
        self.assertIn("Please enter an error message", result)

    def test_unknown_error(self):
        result = explain_error("UnknownProblemXYZ: something happened")
        self.assertIn("could not identify", result.lower())


if __name__ == "__main__":
    unittest.main()
