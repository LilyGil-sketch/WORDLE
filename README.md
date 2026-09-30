# Kids Wordle (Python, CLI)

A command-line version of the word game Wordle, designed for primary school
students and written in plain Python with no external libraries. The secret
word is always one of five simple words - **APPLE, HAPPY, HOUSE, SMILE,
TIGER** - which are shown on the start screen. Guess it in 6 tries; after
each guess the letters are coloured to show how close you are. Messages are
friendly and encouraging, and wrong input gets a gentle "Oops!" tip.

| Colour | Meaning |
|--------|---------|
| Green  | Right letter, right position |
| Yellow | Letter is in the word, but somewhere else |
| Grey   | Letter is not in the word (or no more copies of it) |

## Requirements

- Python 3.8 or newer ([python.org](https://www.python.org/downloads/))
- VS Code with the Python extension (recommended, not required)
- No packages to install - only the Python standard library is used
  (`json`, `os`, `random`, `unittest`)

## How to run

1. Clone or download this repository.
2. Open the folder in VS Code (**File > Open Folder**).
3. Open the terminal (**Terminal > New Terminal**).
4. Run:

   ```bash
   python wordle.py
   ```

   (On macOS/Linux you may need `python3 wordle.py`.)

Type a 5-letter word and press Enter. Type `quit` to give up the current round.

> Tip: run it in the VS Code **terminal**, not the "Output" panel - the
> coloured tiles and screen-clearing need a real terminal.

## How to run the tests

```bash
python -m unittest test_wordle.py -v
```

## Project files

| File | Purpose |
|------|---------|
| `wordle.py` | The game: scoring algorithm, classes and main loop |
| `words.txt` | The five kid-friendly words, one per line - edit to change them |
| `test_wordle.py` | Unit tests for the scoring logic, keyboard and word list |
| `stats.json` | Created automatically after your first game to save your stats |

## How the code works

- **`load_words()`** reads `words.txt` and keeps only valid 5-letter words.
- **`show_rules()`** shows simple instructions and the five possible words.
- **`score_guess()`** is the core algorithm. It uses two passes over the guess:
  the first marks exact matches (green) and counts the leftover letters in the
  answer; the second marks yellows only while leftover copies remain. This is
  what makes repeated letters (e.g. guessing `geese`) behave like real Wordle.
- **`Keyboard` class** remembers the best-known state of every letter and
  never downgrades one (a green key stays green).
- **`Stats` class** saves games played, win %, streaks and a guess
  distribution to `stats.json`, using `try/except` so a missing or corrupted
  file never crashes the game.
- **`WordleGame` class** runs one round: draws the board, validates input and
  checks for a win or loss.
- **`main()`** ties it together and offers to play again.

Colours are produced with ANSI escape codes, which the VS Code terminal
understands on Windows, macOS and Linux.

## Possible future improvements

- Reject guesses that are not real words (a separate "allowed guesses" list)
- A "daily word" mode that picks the same word for everyone each day
- Hard mode: revealed hints must be used in later guesses
