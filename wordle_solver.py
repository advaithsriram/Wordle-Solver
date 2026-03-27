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
from typing import List, Optional, Tuple

# Constants
WORD_LENGTH: int = 5
MAX_TURNS: int = 6
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

    def _get_strategic_guess(self, turn: int, excluded_words: Optional[List[str]] = None) -> str:
        """
        Get a strategic guess based on letter frequency and turn number.
        Avoids previously guessed words.

        Args:
            turn: Current turn number (0-5).
            excluded_words: List of words to exclude from selection (e.g., previously guessed words).

        Returns:
            A word to guess.
        """
        if excluded_words is None:
            excluded_words = []
        
        # Filter out previously guessed words
        available_words = [w for w in self.possible_words if w not in excluded_words]
        
        if not available_words:
            # Fallback: still avoid repeats by using unseen dictionary words first.
            unseen_words = [w for w in self.word_list if w not in excluded_words]
            available_words = unseen_words if unseen_words else self.word_list

        # Early turns prioritize high-frequency-letter probes (e.g., STARE).
        if turn < 2 and len(available_words) > 3:
            return self._select_frequent_word_from(available_words, turn)

        # Later turns converge within the narrowed candidate set.
        return random.choice(available_words)

    def _select_frequent_word_from(self, word_list: List[str], turn: int) -> str:
        """
        Select a word containing the most frequent letters from a given list.

        Args:
            word_list: List of words to choose from.
            turn: Current turn number.

        Returns:
            A word containing frequent letters, or random if none match.
        """
        for i in range(len(self.letter_frequency)):
            frequent_letter = self.letter_frequency[i][0]
            candidates = [w for w in word_list if frequent_letter in w]
            if candidates:
                return random.choice(candidates)
        
        # Fallback: return random word if no frequent letters found
        return random.choice(word_list) if word_list else random.choice(self.possible_words)

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
                
                return self.current_guess, feedback
            
            except Exception as e:
                print(f"Error: {e}. Please try again.")

    def _score_guess_against_target(self, guess: str, target: str) -> str:
        """
        Compute Wordle feedback for a guess against a target word.

        Returns a 5-char string using:
        - '2' for green (correct letter, correct position)
        - '1' for yellow (correct letter, wrong position)
        - '0' for grey (letter not present given remaining counts)
        """
        feedback = ["0"] * WORD_LENGTH
        remaining_letters = Counter()

        # Pass 1: mark greens and count unmatched target letters.
        for idx in range(WORD_LENGTH):
            if guess[idx] == target[idx]:
                feedback[idx] = "2"
            else:
                remaining_letters[target[idx]] += 1

        # Pass 2: mark yellows based on remaining target-letter counts.
        for idx in range(WORD_LENGTH):
            if feedback[idx] != "2":
                letter = guess[idx]
                if remaining_letters[letter] > 0:
                    feedback[idx] = "1"
                    remaining_letters[letter] -= 1

        return "".join(feedback)

    def update_possibilities(self, word_guess: str, feedback: str) -> None:
        """
        Update the list of possible words based on feedback.

        Args:
            word_guess: The guessed word.
            feedback: String of feedback (0, 1, or 2 for each position).
        """
        # Exact Wordle-consistent filtering. This correctly handles duplicates
        # such as VALVE/HALVE/LLAMA edge cases.
        self.possible_words = [
            candidate
            for candidate in self.possible_words
            if self._score_guess_against_target(word_guess, candidate) == feedback
        ]
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
                print(f"\nComputer wins! The word was: {word_guess.upper()}")
                break

            self.update_possibilities(word_guess, feedback)

            if len(self.possible_words) == 0:
                print("\nNo valid words remain. The puzzle may be invalid.")
                break

        if not win:
            print("\nGame Over! Better luck next time.")


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
        


        