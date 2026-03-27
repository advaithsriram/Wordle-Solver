#!/usr/bin/env python3
"""Trainable Wordle strategy solver.

This module defines a small linear model over handcrafted features to choose
Wordle guesses. The weights can be learned by random search and saved to JSON.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from naive.wordle_solver import WORD_LENGTH, WordleSolver


DEFAULT_MODEL = {
    "weights": {
        "unique_freq": 1.0,
        "positional_freq": 1.2,
        "unseen_letters": 0.8,
        "candidate_bonus": 1.0,
        "duplicate_penalty": 1.5,
    },
    "explore_turns": 2,
}


class TrainedWordleSolver(WordleSolver):
    """Wordle solver that scores guesses with a trainable linear strategy model."""

    def __init__(self, model_path: Optional[str] = None, model: Optional[Dict] = None) -> None:
        super().__init__()
        if model is not None:
            self.model = model
        elif model_path:
            self.model = self.load_model(model_path)
        else:
            self.model = DEFAULT_MODEL

    @staticmethod
    def load_model(path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_model(path: str, model: Dict) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(model, file, indent=2)

    def _build_global_letter_freq(self) -> Dict[str, int]:
        freq: Dict[str, int] = {}
        for word in self.possible_words:
            for ch in word:
                freq[ch] = freq.get(ch, 0) + 1
        return freq

    def _build_positional_freq(self) -> List[Dict[str, int]]:
        pos = [dict() for _ in range(WORD_LENGTH)]
        for word in self.possible_words:
            for idx, ch in enumerate(word):
                pos[idx][ch] = pos[idx].get(ch, 0) + 1
        return pos

    def _score_word(
        self,
        word: str,
        guessed_letters: set,
        in_candidate_pool: bool,
        global_freq: Dict[str, int],
        positional_freq: List[Dict[str, int]],
    ) -> float:
        w = self.model["weights"]

        unique_letters = set(word)
        duplicate_count = len(word) - len(unique_letters)

        unique_freq_score = sum(global_freq.get(ch, 0) for ch in unique_letters)
        positional_score = sum(positional_freq[idx].get(ch, 0) for idx, ch in enumerate(word))
        unseen_bonus = sum(1 for ch in unique_letters if ch not in guessed_letters)
        candidate_bonus = 1 if in_candidate_pool else 0

        score = 0.0
        score += w["unique_freq"] * unique_freq_score
        score += w["positional_freq"] * positional_score
        score += w["unseen_letters"] * unseen_bonus
        score += w["candidate_bonus"] * candidate_bonus
        score -= w["duplicate_penalty"] * duplicate_count
        return score

    def _get_strategic_guess(self, turn: int, excluded_words: Optional[List[str]] = None) -> str:
        if excluded_words is None:
            excluded_words = []

        candidate_pool = [w for w in self.possible_words if w not in excluded_words]

        # Early exploration can use the full dictionary to gather information,
        # later turns should converge on candidate solutions.
        explore_turns = int(self.model.get("explore_turns", 2))
        if turn < explore_turns:
            full_pool = [w for w in self.word_list if w not in excluded_words]
            scoring_pool = full_pool if full_pool else candidate_pool
        else:
            scoring_pool = candidate_pool

        if not scoring_pool:
            return self.word_list[0]

        guessed_letters = set("".join(excluded_words))
        global_freq = self._build_global_letter_freq()
        positional_freq = self._build_positional_freq()
        candidate_set = set(candidate_pool)

        best_word = None
        best_score = None
        for word in scoring_pool:
            score = self._score_word(
                word=word,
                guessed_letters=guessed_letters,
                in_candidate_pool=(word in candidate_set),
                global_freq=global_freq,
                positional_freq=positional_freq,
            )
            # Deterministic tie-break by lexical order for reproducibility.
            if best_score is None or score > best_score or (score == best_score and word < best_word):
                best_score = score
                best_word = word

        return best_word if best_word is not None else scoring_pool[0]
