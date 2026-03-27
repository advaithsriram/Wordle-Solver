#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wordle Solver - An AI-powered solver for the Wordle game.

This module provides a class-based implementation of a Wordle puzzle solver
that uses letter frequency analysis and elimination strategies to guess
the correct word within 6 attempts.

Author: advaith
"""

import random
from collections import Counter
from typing import List, Tuple

# Constants
WORD_LENGTH: int = 5
MAX_TURNS: int = 6
PERFECT_SCORE: int = 22222  # 5 positions * score of 2 (green)
WORD_FILE: str = "wordle_words.txt"

# Letter Score Constants
GREY: int = 0  # Letter not in word
YELLOW: int = 1  # Letter in word, wrong position
GREEN: int = 2  # Letter in word, correct position


class WordleSolver:
    """
    A class to solve Wordle puzzles using frequency analysis and elimination.
    """

    def __init__(self, word_file: str = WORD_FILE) -> None:
        """
        Initialize the Wordle Solver.

        Args:
            word_file: Path to the file containing valid Wordle words.
        """
        self.word_file = word_file
        self.word_list: List[str] = []
        self.possible_words: List[str] = []
        self.letter_frequency: List[Tuple[str, int]] = []
        self.total_score: int = 0
        self.current_guess: str = ""

    def load_words(self) -> None:
        """Load words from file and initialize the word list."""
        try:
            with open(self.word_file, 'r') as file:
                self.word_list = [line.rstrip().lower() for line in file]
            
            if not self.word_list:
                raise ValueError("Word list is empty")
            
            self.possible_words = self.word_list.copy()
            self._update_letter_frequency()
        except FileNotFoundError:
            print(f"Error: {self.word_file} not found.")
            raise
        except Exception as e:
            print(f"Error loading words: {e}")
            raise

    def _update_letter_frequency(self) -> None:
        """
        Update letter frequency based on current possible words.
        This dynamic update improves guessing strategy as possibilities shrink.
        """
        combined_string = "".join(self.possible_words)
        letter_counts = Counter(combined_string)
        # Sort by frequency in descending order
        self.letter_frequency = letter_counts.most_common()

    def _get_strategic_guess(self, turn: int) -> str:
        """
        Get a strategic guess based on letter frequency and turn number.

        Args:
            turn: Current turn number (0-5).

        Returns:
            A word to guess.
        """
        if self.total_score <= 4 and len(self.possible_words) > 3:
            # Early game with high-frequency letters
            return self._select_frequent_word(turn)
        else:
            # Random selection from remaining possibilities
            return random.choice(self.possible_words)

    def _select_frequent_word(self, turn: int) -> str:
        """
        Select a word containing the most frequent letters.

        Args:
            turn: Current turn number.

        Returns:
            A word containing frequent letters, or random if none match.
        """
        for i in range(len(self.letter_frequency)):
            frequent_letter = self.letter_frequency[i][0]
            candidates = [w for w in self.possible_words if frequent_letter in w]
            if candidates:
                return random.choice(candidates)
        
        # Fallback: return random word if no frequent letters found
        return random.choice(self.possible_words) if self.possible_words else random.choice(self.word_list)

    def make_guess(self, turn: int) -> Tuple[str, str]:
        """
        Make a guess and collect user feedback.

        Args:
            turn: Current turn number (0-5).

        Returns:
            Tuple of (guessed_word, feedback_string).
        """
        self.current_guess = self._get_strategic_guess(turn)
        confidence_value = self._calculate_confidence()
        
        print(f"\nThe computer's guess is:\n  {self.current_guess.upper()}")
        print(f"  Confidence Value: {confidence_value:.2f}%\n")
        
        while True:
            try:
                feedback = input("Enter result of guess (grey=0, yellow=1, green=2, Ex. 02002): ").strip()
                
                if len(feedback) != WORD_LENGTH or not feedback.isdigit():
                    print(f"Invalid input. Please enter exactly {WORD_LENGTH} digits (0, 1, or 2).")
                    continue
                
                if not all(c in '012' for c in feedback):
                    print("Invalid input. Each digit must be 0 (grey), 1 (yellow), or 2 (green).")
                    continue
                
                # Update total score
                for digit in feedback:
                    self.total_score += int(digit)
                
                return self.current_guess, feedback
            
            except Exception as e:
                print(f"Error: {e}. Please try again.")

    def update_possibilities(self, word_guess: str, feedback: str) -> None:
        """
        Update the list of possible words based on feedback.

        Args:
            word_guess: The guessed word.
            feedback: String of feedback (0, 1, or 2 for each position).
        """
        new_possibilities = self.possible_words.copy()

        for pos, (letter, score_char) in enumerate(zip(word_guess, feedback)):
            score = int(score_char)

            if score == GREY:
                # Letter is not in the word (unless it appears elsewhere)
                letter_positions = [i for i, c in enumerate(word_guess) if c == letter]
                
                # Check if letter appears in other positions with green/yellow
                has_other_match = any(int(feedback[i]) > GREY for i in letter_positions if i != pos)
                
                if not has_other_match:
                    new_possibilities = [w for w in new_possibilities if letter not in w]

            elif score == YELLOW:
                # Letter is in word but wrong position
                new_possibilities = [w for w in new_possibilities if letter in w and w[pos] != letter]

            elif score == GREEN:
                # Letter is in correct position
                new_possibilities = [w for w in new_possibilities if w[pos] == letter]

        self.possible_words = new_possibilities
        self._update_letter_frequency()

    def _calculate_confidence(self) -> float:
        """
        Calculate confidence as a percentage based on remaining possibilities.

        Returns:
            Confidence percentage (0-100).
        """
        if len(self.possible_words) == 0:
            return 0.0
        return 100.0 / len(self.possible_words)

    def play(self) -> None:
        """Run the Wordle solving game."""
        print("=" * 50)
        print("Welcome to Wordle Solver!")
        print("=" * 50)
        print(f"Starting with {len(self.word_list)} possible words.\n")

        self.load_words()
        win = False

        for turn in range(MAX_TURNS):
            print(f"Turn {turn + 1}/{MAX_TURNS} - Remaining possibilities: {len(self.possible_words)}")
            
            word_guess, feedback = self.make_guess(turn)

            # Check for win (all green)
            if feedback == "2" * WORD_LENGTH:
                win = True
                print(f"\n🎉 Computer wins! The word was: {word_guess.upper()}")
                print(f"Final score: {self.total_score}")
                break

            self.update_possibilities(word_guess, feedback)

            if len(self.possible_words) == 0:
                print("\n❌ No valid words remain. The puzzle may be invalid.")
                break

        if not win:
            print(f"\n😢 Game Over! Better luck next time.")
            print(f"Total score: {self.total_score}")


def debug_solver() -> None:
    """Debug the solver with predefined test cases."""
    print("\n=== DEBUGGING MODE ===\n")
    solver = WordleSolver()
    solver.load_words()

    test_cases = [
        ("those", "00200"),
        ("brain", "00000"),
        ("brunt", "00000"),
        ("lumpy", "10000"),
        ("lease", "10000"),
    ]

    for word, feedback in test_cases:
        print(f"Guessed: {word}, Feedback: {feedback}")
        solver.update_possibilities(word, feedback)
        print(f"Remaining: {len(solver.possible_words)} words\n")

    print(f"Final possibilities: {solver.possible_words[:10]}...")


if __name__ == "__main__":
    solver = WordleSolver()
    solver.play()
    
    # Uncomment below to run debug mode:
    # debug_solver()
        


        