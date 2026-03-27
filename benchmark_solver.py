#!/usr/bin/env python3
"""Benchmark the Wordle solver success rate.

This script simulates full Wordle games across the dictionary and reports:
- solve rate
- average turns for solved words
- failed words
- hardest words across multiple random seeds

Usage examples:
  python benchmark_solver.py
  python benchmark_solver.py --num-seeds 10 --seed-start 0
  python benchmark_solver.py --word-limit 500 --sample-failed 20
  python benchmark_solver.py --json-out benchmark_results.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from statistics import mean
from typing import Dict, List, Tuple

from wordle_solver import MAX_TURNS, WordleSolver


def simulate_target(target: str, seed: int) -> Tuple[bool, int]:
    """Simulate one game against a specific target word for one random seed."""
    import random

    random.seed(seed)
    solver = WordleSolver()
    solver.load_words()

    guessed_words: List[str] = []
    for turn in range(MAX_TURNS):
        guess = solver._get_strategic_guess(turn, guessed_words)
        guessed_words.append(guess)

        feedback = solver._score_guess_against_target(guess, target)
        if feedback == "2" * 5:
            return True, turn + 1

        solver.update_possibilities(guess, feedback)

    return False, MAX_TURNS


def run_single_seed(words: List[str], seed: int) -> Dict[str, object]:
    """Run full benchmark for one seed across all words."""
    results = [(word, *simulate_target(word, seed=seed)) for word in words]
    failed_words = [word for word, solved, _turns in results if not solved]
    solved_turns = [turns for _word, solved, turns in results if solved]

    solved_count = len(solved_turns)
    failed_count = len(failed_words)
    total_words = len(words)

    return {
        "seed": seed,
        "total_words": total_words,
        "solved_count": solved_count,
        "failed_count": failed_count,
        "solve_rate": solved_count / total_words if total_words else 0.0,
        "avg_turns_solved": mean(solved_turns) if solved_turns else None,
        "max_turns_solved": max(solved_turns) if solved_turns else None,
        "failed_words": failed_words,
    }


def run_multi_seed_hardness(words: List[str], seeds: List[int]) -> List[Tuple[str, int]]:
    """Count how many seeds fail for each word and return sorted hard-word list."""
    fail_count = defaultdict(int)

    for word in words:
        for seed in seeds:
            solved, _turns = simulate_target(word, seed=seed)
            if not solved:
                fail_count[word] += 1

    hard_words = sorted(
        ((word, count) for word, count in fail_count.items() if count > 0),
        key=lambda item: (-item[1], item[0]),
    )
    return hard_words


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def write_notes_markdown(
    notes_path: str,
    single: Dict[str, object],
    hard_words: List[Tuple[str, int]],
    seeds: List[int],
    top_hard: int,
) -> None:
    """Overwrite notes.md with the latest benchmark results."""
    failed_words: List[str] = single["failed_words"]  # type: ignore[assignment]
    avg_turns = single["avg_turns_solved"]
    avg_turns_str = f"{avg_turns:.3f}" if avg_turns is not None else "N/A"

    lines: List[str] = []
    lines.append("# Solver Benchmark Notes")
    lines.append("")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append("")
    lines.append("## Current Solver Results")
    lines.append("")
    lines.append(f"- Seed: {single['seed']}")
    lines.append(f"- Total words tested: {single['total_words']}")
    lines.append(f"- Solved within 6 turns: {single['solved_count']}")
    lines.append(f"- Failed within 6 turns: {single['failed_count']}")
    lines.append(f"- Solve rate: {format_pct(single['solve_rate'])}")
    lines.append(f"- Average turns (solved words): {avg_turns_str}")
    lines.append(f"- Max turns used on solved words: {single['max_turns_solved']}")
    lines.append("")
    lines.append("## Failed Words")
    lines.append("")
    if failed_words:
        for word in failed_words:
            lines.append(f"- {word}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Multi-Seed Hard Words")
    lines.append("")
    lines.append(f"- Seeds: {seeds[0]}..{seeds[-1]} ({len(seeds)} total)")
    lines.append(f"- Words failing at least once across those seeds: {len(hard_words)}")
    lines.append("")
    lines.append(f"Top {top_hard} hard words (word, failed_seeds):")
    lines.append("")
    for word, count in hard_words[:top_hard]:
        lines.append(f"- {word}: {count}")

    with open(notes_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Wordle solver performance.")
    parser.add_argument("--seed", type=int, default=42, help="Primary seed for single-seed report.")
    parser.add_argument("--num-seeds", type=int, default=10, help="Number of seeds for hard-word analysis.")
    parser.add_argument("--seed-start", type=int, default=0, help="First seed for hard-word analysis.")
    parser.add_argument("--word-limit", type=int, default=0, help="Limit number of words for faster test (0 = all).")
    parser.add_argument("--sample-failed", type=int, default=30, help="How many failed words to print from single-seed run.")
    parser.add_argument("--top-hard", type=int, default=40, help="How many hard words to print from multi-seed run.")
    parser.add_argument("--notes-out", type=str, default="notes.md", help="Path to overwrite markdown notes output.")
    parser.add_argument("--json-out", type=str, default="", help="Optional JSON output path.")
    args = parser.parse_args()

    template_solver = WordleSolver()
    template_solver.load_words()
    words = template_solver.word_list

    if args.word_limit > 0:
        words = words[: args.word_limit]

    seeds = list(range(args.seed_start, args.seed_start + max(1, args.num_seeds)))

    single = run_single_seed(words, seed=args.seed)
    hard_words = run_multi_seed_hardness(words, seeds=seeds)

    print("=== Single-Seed Report ===")
    print(f"Seed: {single['seed']}")
    print(f"Words tested: {single['total_words']}")
    print(f"Solved: {single['solved_count']}")
    print(f"Failed: {single['failed_count']}")
    print(f"Solve rate: {format_pct(single['solve_rate'])}")
    print(f"Avg turns (solved): {single['avg_turns_solved']:.3f}" if single["avg_turns_solved"] is not None else "Avg turns (solved): N/A")
    print(f"Max turns (solved): {single['max_turns_solved']}")

    failed_words = single["failed_words"]
    if failed_words:
        print(f"Sample failed words (first {args.sample_failed}):")
        print(failed_words[: args.sample_failed])
    else:
        print("No failures in single-seed run.")

    print("\n=== Multi-Seed Hard-Word Report ===")
    print(f"Seeds: {seeds[0]}..{seeds[-1]} ({len(seeds)} total)")
    print(f"Words that failed at least once: {len(hard_words)}")
    print(f"Top {args.top_hard} hard words (word, failed_seeds):")
    print(hard_words[: args.top_hard])

    write_notes_markdown(
        notes_path=args.notes_out,
        single=single,
        hard_words=hard_words,
        seeds=seeds,
        top_hard=args.top_hard,
    )
    print(f"\nUpdated markdown notes: {args.notes_out}")

    if args.json_out:
        payload = {
            "single_seed": {
                "seed": single["seed"],
                "total_words": single["total_words"],
                "solved_count": single["solved_count"],
                "failed_count": single["failed_count"],
                "solve_rate": single["solve_rate"],
                "avg_turns_solved": single["avg_turns_solved"],
                "max_turns_solved": single["max_turns_solved"],
                "failed_words": single["failed_words"],
            },
            "multi_seed": {
                "seeds": seeds,
                "hard_words": hard_words,
            },
        }
        with open(args.json_out, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)
        print(f"\nSaved JSON report to: {args.json_out}")


if __name__ == "__main__":
    main()
