"""
Unit tests for Kids Wordle.
Run in the VS Code terminal with:
    python -m unittest test_wordle.py -v

Each test checks one small behaviour. If a later change breaks
the scoring logic, these tests will catch it straight away.
"""
# Import Python's built-in testing tool
import unittest

# Import the pieces we want to test from the main game file,
# giving the colour states short names (G = green, Y = yellow, X = grey)
from wordle import score_guess, load_words, Keyboard, WORD_FILE
from wordle import CORRECT as G, PRESENT as Y, ABSENT as X


# Tests for the scoring algorithm
class TestScoreGuess(unittest.TestCase):

    # Guessing the answer exactly should give five greens
    def test_all_correct(self):
        self.assertEqual(score_guess("tiger", "tiger"), [G, G, G, G, G])

    # A guess sharing no letters with the answer should be all grey
    def test_all_absent(self):
        self.assertEqual(score_guess("dunky", "apple"), [X, X, X, X, X])

    # A mix: h, o, s, e match "house" exactly; 'r' is not in "house"
    def test_mixed(self):
        self.assertEqual(score_guess("horse", "house"), [G, G, X, G, G])

    # Letters in the wrong spot should be yellow
    def test_wrong_spots(self):
        # "smile" and "limes" use the same letters in different places
        self.assertEqual(score_guess("limes", "smile"), [Y, Y, Y, Y, Y])

    # "apple" has two p's: the green 'p' uses up one copy,
    # so the spare copy lets the other 'p' in "happy" turn yellow
    def test_double_letters(self):
        self.assertEqual(score_guess("happy", "apple"), [X, Y, G, Y, X])

    # "tiger" has one 'e': only the first 'e' in "geese" turns yellow,
    # and the extra e's go grey
    def test_extra_copies_go_grey(self):
        self.assertEqual(score_guess("geese", "tiger"), [Y, Y, X, X, X])


# Tests for the on-screen keyboard
class TestKeyboard(unittest.TestCase):

    # A key that has been green should stay green, even after a yellow
    def test_state_never_downgrades(self):
        kb = Keyboard()
        kb.update("tiger", [G, X, X, X, X])
        kb.update("otter", [X, Y, X, X, X])
        self.assertEqual(kb.letters["t"], G)


# Tests for the word list file
class TestWordList(unittest.TestCase):

    # The kids' list should hold exactly five valid 5-letter words
    def test_five_simple_words(self):
        words = load_words(WORD_FILE)
        self.assertEqual(len(words), 5)
        for word in words:
            self.assertEqual(len(word), 5)
            self.assertTrue(word.isalpha())


# Run all the tests when this file is run directly
if __name__ == "__main__":
    unittest.main()
