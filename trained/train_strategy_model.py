#!/usr/bin/env python3
"""Train a small linear strategy model for Wordle.

This script performs random-search training over model weights used by
TrainedWordleSolver and saves the best model to JSON.
"""

from __future__ import annotations

import argparse
import random
from statistics import mean
from typing import Dict, List, Tuple

from naive.wordle_solver import MAX_TURNS
from trained.trained_solver import DEFAULT_MODEL, TrainedWordleSolver


def simulate_target(target: str, model: Dict, seed: int = 0) -> Tuple[bool, int]:
    random.seed(seed)
    solver = TrainedWordleSolver(model=model)
    solver.load_words()

    guessed_words: List[str] = []
    for turn in range(MAX_TURNS):
        guess = solver._get_strategic_guess(turn, guessed_words)
        guessed_words.append(guess)
        feedback = solver._score_guess_against_target(guess, target)
        if feedback == "22222":
            return True, turn + 1
        solver.update_possibilities(guess, feedback)
    return False, MAX_TURNS


def evaluate_model(words: List[str], model: Dict, seed: int = 0) -> Dict[str, float]:
    solved_turns: List[int] = []
    failed = 0
    for w in words:
        solved, turns = simulate_target(w, model, seed=seed)
        if solved:
            solved_turns.append(turns)
        else:
            failed += 1

    total = len(words)
    solved = len(solved_turns)
    solve_rate = solved / total if total else 0.0
    avg_turns = mean(solved_turns) if solved_turns else float(MAX_TURNS)

    # Strongly penalize failures first, then optimize turns.
    score = (solve_rate * 1000.0) - (avg_turns * 10.0) - (failed * 5.0)
    return {
        "score": score,
        "solve_rate": solve_rate,
        "avg_turns": avg_turns,
        "failed": float(failed),
    }


def mutate_model(base_model: Dict, step: float, rng: random.Random) -> Dict:
    model = {
        "weights": dict(base_model["weights"]),
        "explore_turns": int(base_model.get("explore_turns", 2)),
    }

    for key, value in model["weights"].items():
        delta = rng.uniform(-step, step)
        new_value = max(0.0, value + delta)
        model["weights"][key] = new_value

    # Occasionally mutate exploration depth.
    if rng.random() < 0.2:
        model["explore_turns"] = max(0, min(4, model["explore_turns"] + rng.choice([-1, 1])))

    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a small Wordle strategy model.")
    parser.add_argument("--iterations", type=int, default=200, help="Random-search iterations.")
    parser.add_argument("--train-size", type=int, default=600, help="Number of words used for training.")
    parser.add_argument("--eval-size", type=int, default=300, help="Number of words used for holdout eval.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducibility.")
    parser.add_argument("--step", type=float, default=0.35, help="Mutation step size.")
    parser.add_argument("--out", type=str, default="trained/trained_strategy.json", help="Output JSON path.")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    base_solver = TrainedWordleSolver(model=DEFAULT_MODEL)
    base_solver.load_words()
    words = list(base_solver.word_list)
    rng.shuffle(words)

    train_words = words[: args.train_size]
    eval_words = words[args.train_size : args.train_size + args.eval_size]

    best_model = {
        "weights": dict(DEFAULT_MODEL["weights"]),
        "explore_turns": int(DEFAULT_MODEL["explore_turns"]),
    }
    best_train = evaluate_model(train_words, best_model, seed=args.seed)

    for i in range(1, args.iterations + 1):
        candidate = mutate_model(best_model, args.step, rng)
        candidate_metrics = evaluate_model(train_words, candidate, seed=args.seed)
        if candidate_metrics["score"] > best_train["score"]:
            best_model = candidate
            best_train = candidate_metrics

        if i % 25 == 0 or i == args.iterations:
            print(
                f"iter={i} score={best_train['score']:.2f} "
                f"solve_rate={best_train['solve_rate']:.4f} "
                f"avg_turns={best_train['avg_turns']:.3f} "
                f"failed={int(best_train['failed'])}"
            )

    eval_metrics = evaluate_model(eval_words, best_model, seed=args.seed)
    best_model["train_metrics"] = best_train
    best_model["eval_metrics"] = eval_metrics
    best_model["train_config"] = {
        "iterations": args.iterations,
        "train_size": args.train_size,
        "eval_size": args.eval_size,
        "seed": args.seed,
        "step": args.step,
    }

    TrainedWordleSolver.save_model(args.out, best_model)

    print("\nSaved model:", args.out)
    print("Best weights:", best_model["weights"])
    print("Train metrics:", best_train)
    print("Eval metrics:", eval_metrics)


if __name__ == "__main__":
    main()
