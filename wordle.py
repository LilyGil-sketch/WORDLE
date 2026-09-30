"""
==============================================================
 KIDS WORDLE  -  a word-guessing game for primary school students
==============================================================
How to run (in the VS Code terminal):
    python wordle.py

How the game works:
    - The computer secretly picks one of five simple words.
    - You have 6 guesses to find it.
    - After each guess, every letter is coloured:
        GREEN  = right letter, right spot
        YELLOW = the letter is in the word, but in a different spot
        GREY   = the letter is not in the word

Code structure (overview):
    Constants          -> settings used throughout the program
    load_words()       -> reads the word list from a text file
    score_guess()      -> the core algorithm that colours a guess
    colour_tile()      -> turns a letter + state into coloured text
    class Keyboard     -> remembers what we know about every letter
    class Stats        -> saves and loads player statistics (JSON file)
    class WordleGame   -> runs one full round of the game
    main()             -> the menu loop that ties everything together
"""

# ============================================================
# IMPORTS
# ============================================================

# Import modules from Python's standard library (nothing to install)
import json      # read/write the stats file in JSON format
import os        # file paths and clearing the screen
import random    # choosing the secret word


# ============================================================
# CONSTANTS - values in CAPITALS never change while the game runs
# ============================================================

# Game rules: how long each word is and how many guesses a player gets
WORD_LENGTH = 5
MAX_GUESSES = 6

# Build file paths from this script's own folder, so the game finds its
# files no matter which folder it is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORD_FILE = os.path.join(BASE_DIR, "words.txt")
STATS_FILE = os.path.join(BASE_DIR, "stats.json")

# Name the possible states of a letter, so we never mistype a raw string
CORRECT = "correct"   # green
PRESENT = "present"   # yellow
ABSENT = "absent"     # grey
UNUSED = "unused"     # letter not guessed yet (keyboard only)

# ANSI colour codes: special text the terminal reads as colour commands
# (42m = green background, 43m = yellow, 100m = dark grey, 30m = black text)
RESET = "\033[0m"
COLOURS = {
    CORRECT: "\033[42m\033[30m",  # black text on green
    PRESENT: "\033[43m\033[30m",  # black text on yellow
    ABSENT: "\033[100m\033[97m",  # white text on dark grey
    UNUSED: "\033[47m\033[30m",   # black text on light grey
}

# Friendly messages for winning, chosen by how many guesses it took
# (a list: index 0 is used for 1 guess, index 1 for 2 guesses, and so on)
WIN_MESSAGES = [
    "WOW! First try - you're a word wizard!",
    "Amazing! Only two guesses!",
    "Super job! You got it in three!",
    "Great work! Four guesses!",
    "Well done! You worked it out!",
    "Phew! Just in time - you did it!",
]

# Switch on colour support in older Windows terminals (harmless elsewhere)
if os.name == "nt":
    os.system("")


# ============================================================
# FUNCTIONS - small reusable blocks of code
# ============================================================

def load_words(path):
    """Read the word file and return a list of valid 5-letter words."""
    # Start with an empty list to collect the words in
    words = []

    # Open the file and look at it one line at a time
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            # Tidy the line: remove spaces/newlines and make it lowercase
            word = line.strip().lower()

            # Only keep words that are exactly 5 letters long
            if len(word) == WORD_LENGTH and word.isalpha():
                words.append(word)

    # Give the finished list back to whoever called this function
    return words


def score_guess(guess, answer):
    """Compare a guess with the answer. Returns a list of 5 states,
    e.g. [CORRECT, ABSENT, PRESENT, ABSENT, CORRECT]."""
    # Start by assuming every letter is wrong (grey)
    result = [ABSENT] * WORD_LENGTH

    # Make a dictionary to count answer letters that are NOT exact matches
    # (only these letters are allowed to turn yellow later)
    remaining = {}

    # PASS 1: find letters in exactly the right spot and make them green
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i]:
            result[i] = CORRECT
        else:
            remaining[answer[i]] = remaining.get(answer[i], 0) + 1

    # PASS 2: find letters that are in the word but in the wrong spot
    for i in range(WORD_LENGTH):
        # Skip letters that are already green
        if result[i] == CORRECT:
            continue

        # Turn the letter yellow if a spare copy is left, then use it up
        letter = guess[i]
        if remaining.get(letter, 0) > 0:
            result[i] = PRESENT
            remaining[letter] -= 1

    # Send back the finished list of colours
    return result


def colour_tile(letter, state):
    """Return one letter as a coloured tile, e.g. ' A ' on green."""
    # Wrap the capital letter in its colour code, then reset the colour
    return f"{COLOURS[state]} {letter.upper()} {RESET}"


def clear_screen():
    """Clear the terminal so the board redraws cleanly each turn."""
    # Windows uses 'cls'; macOS and Linux use 'clear'
    os.system("cls" if os.name == "nt" else "clear")


def show_rules(word_list):
    """Print simple instructions for young players."""
    # Explain the colours and show every word the game might pick
    clear_screen()
    print("===========  KIDS WORDLE  ===========\n")
    print("Can you guess the secret 5-letter word?")
    print(f"You have {MAX_GUESSES} tries.\n")
    print(colour_tile("a", CORRECT), "Green  = right letter, right spot")
    print(colour_tile("b", PRESENT), "Yellow = in the word, wrong spot")
    print(colour_tile("c", ABSENT), "Grey   = not in the word\n")
    print("The secret word is one of these:")
    print("   " + "   ".join(word.upper() for word in word_list))

    # Wait for the player to be ready before starting
    input("\nPress Enter to start...")


# ============================================================
# CLASSES - blueprints that bundle data and the code that uses it
# ============================================================

class Keyboard:
    """Remembers what we know about every letter A-Z and draws it
    as an on-screen keyboard."""

    # The three rows of a QWERTY keyboard, stored as a list of strings
    ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]

    # Rank the states so a key can go up (grey -> yellow -> green)
    # but never back down
    PRIORITY = {UNUSED: 0, ABSENT: 1, PRESENT: 2, CORRECT: 3}

    def __init__(self):
        # Set every letter A-Z to "unused" when a new keyboard is made
        self.letters = {ch: UNUSED for ch in "abcdefghijklmnopqrstuvwxyz"}

    def update(self, guess, states):
        """Record the result of a guess, keeping the best state."""
        # Pair each letter with its colour and upgrade the key if better
        for letter, state in zip(guess, states):
            if self.PRIORITY[state] > self.PRIORITY[self.letters[letter]]:
                self.letters[letter] = state

    def display(self):
        """Print the keyboard with each key coloured by its state."""
        # Draw each row, indenting it a little more like a real keyboard
        for indent, row in enumerate(self.ROWS):
            keys = "".join(colour_tile(ch, self.letters[ch]) for ch in row)
            print("  " * indent + keys)


class Stats:
    """Loads, updates and saves the player's scores in a JSON file,
    so they are remembered next time the game is opened."""

    def __init__(self, path):
        # Remember where the stats file lives, then load what's in it
        self.path = path
        self.data = self.load()

    def default_data(self):
        """The starting stats for a brand-new player."""
        # Everything starts at zero; distribution counts wins per guess
        return {
            "played": 0,
            "wins": 0,
            "current_streak": 0,
            "max_streak": 0,
            "distribution": {str(n): 0 for n in range(1, MAX_GUESSES + 1)},
        }

    def load(self):
        """Read stats from the file, or start fresh if there isn't one."""
        # try/except stops the game crashing if the file is missing or broken
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_data()

    def save(self):
        """Write the current stats back to the JSON file."""
        # Save the dictionary as neatly indented JSON text
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)

    def record(self, won, guesses_used):
        """Update the stats after a game, then save them."""
        # Count every game played
        self.data["played"] += 1

        # On a win: add to wins, grow the streak, and log the guess count
        if won:
            self.data["wins"] += 1
            self.data["current_streak"] += 1
            self.data["max_streak"] = max(self.data["max_streak"],
                                          self.data["current_streak"])
            self.data["distribution"][str(guesses_used)] += 1

        # On a loss: the winning streak goes back to zero
        else:
            self.data["current_streak"] = 0

        # Store the new totals in the file
        self.save()

    def display(self):
        """Print the scores and a simple bar chart."""
        # Work out the win percentage (avoid dividing by zero)
        played = self.data["played"]
        win_rate = round(self.data["wins"] / played * 100) if played else 0

        # Print the summary line
        print("\n========  YOUR SCORES  ========")
        print(f"Played: {played}   Won: {win_rate}%   "
              f"Streak: {self.data['current_streak']}   "
              f"Best streak: {self.data['max_streak']}")

        # Draw a bar of * for each guess count (longest bar = 20 stars)
        print("\nHow many guesses you needed:")
        dist = self.data["distribution"]
        biggest = max(dist.values()) or 1
        for guesses, count in dist.items():
            bar = "*" * round(count / biggest * 20)
            print(f"  {guesses} | {bar} {count}")


class WordleGame:
    """Runs one round: picks a word, takes guesses, shows the board."""

    def __init__(self, word_list):
        # Choose the secret word at random from the list
        self.word_list = word_list
        self.answer = random.choice(word_list)

        # Set up empty lists for the guesses and their colours,
        # and give this game its own fresh keyboard
        self.guesses = []
        self.results = []
        self.keyboard = Keyboard()

    def draw_board(self):
        """Print all guesses so far, plus empty rows still to play."""
        # Clear the screen and print the title
        clear_screen()
        print("===========  KIDS WORDLE  ===========\n")

        # Draw each of the 6 rows: coloured if guessed, blank if not
        for row in range(MAX_GUESSES):
            if row < len(self.guesses):
                tiles = "".join(colour_tile(letter, state) for letter, state
                                in zip(self.guesses[row], self.results[row]))
            else:
                tiles = " _ " * WORD_LENGTH
            print("       " + tiles)

        # Show the keyboard underneath the board
        print()
        self.keyboard.display()
        print()

    def get_valid_guess(self):
        """Keep asking until the player types a good guess.
        Returns the guess, or None if the player types 'quit'."""
        # Loop forever until a good guess is typed
        while True:
            # Ask for a guess and tidy it up
            guess = input(f"Guess {len(self.guesses) + 1} of {MAX_GUESSES} "
                          "(or type quit): ").strip().lower()

            # Check the guess and give a friendly tip if something is wrong
            if guess == "quit":
                return None
            if len(guess) != WORD_LENGTH:
                print(f"  Oops! Your word needs {WORD_LENGTH} letters.")
            elif not guess.isalpha():
                print("  Oops! Use letters only - no numbers or spaces.")
            elif guess in self.guesses:
                print("  You already tried that one - try a new word!")
            else:
                return guess

    def play(self):
        """The main game loop. Returns (won, number_of_guesses)."""
        # Keep playing while the player still has guesses left
        while len(self.guesses) < MAX_GUESSES:
            # Show the board and get the next guess
            self.draw_board()
            guess = self.get_valid_guess()

            # Stop the round early if the player typed 'quit'
            if guess is None:
                print(f"\nThe secret word was {self.answer.upper()}.")
                return False, len(self.guesses)

            # Colour the guess and remember it on the board and keyboard
            states = score_guess(guess, self.answer)
            self.guesses.append(guess)
            self.results.append(states)
            self.keyboard.update(guess, states)

            # Check for a win and cheer with a message that suits the score
            if guess == self.answer:
                self.draw_board()
                print(WIN_MESSAGES[len(self.guesses) - 1])
                return True, len(self.guesses)

        # Out of guesses: reveal the word kindly
        self.draw_board()
        print(f"Good try! The secret word was {self.answer.upper()}.")
        print("Have another go - you'll get it next time!")
        return False, len(self.guesses)


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    """Load everything, then play games until the player stops."""
    # Load the word list, stopping with a message if the file is missing
    try:
        words = load_words(WORD_FILE)
    except FileNotFoundError:
        print(f"Could not find the word list at {WORD_FILE}")
        return

    # Stop if the file had no usable 5-letter words
    if not words:
        print("The word list is empty - add some 5-letter words to words.txt")
        return

    # Load the saved scores and show the rules
    stats = Stats(STATS_FILE)
    show_rules(words)

    # Play a round, record the result, show scores, then ask to play again
    while True:
        game = WordleGame(words)
        won, used = game.play()
        stats.record(won, used)
        stats.display()

        # Leave the loop unless the player types y
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! See you next time!")
            break


# Only start the game when this file is run directly
# (not when it is imported by the test file)
if __name__ == "__main__":
    main()
