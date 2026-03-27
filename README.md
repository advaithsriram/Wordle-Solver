# Wordle-Solver
A Python Wordle project with a naive heuristic solver, interactive UI, and benchmark tooling.

## Features
- Naive heuristic word guessing using letter frequency and elimination
- Interactive Streamlit web UI with color-coded feedback
- Real-time confidence tracking and word possibility updates
- Automated benchmark runner with notes and "hard"-word reporting

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup
1. Clone or download the repository
2. Navigate to the project directory
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Interactive Web UI (Recommended)
Run the Streamlit interface for an interactive, user-friendly experience:
```bash
streamlit run wordle_ui.py
```

This will open a web browser at `http://localhost:8501` with an interactive interface where you can:
- See the suggested word displayed as large tiles
- Click color buttons (⬜🟨🟩) to provide feedback
- Watch real-time updates on confidence and remaining possibilities
- Track your game history

### Option 2: Command Line Interface
For the original command-line version:
```bash
python wordle_solver.py
```

Then follow the prompts to enter feedback as:
- **0** for Grey (not in word)
- **1** for Yellow (wrong position)
- **2** for Green (correct position)

### Option 3: Benchmark Solver (Auto Simulation)
Run the benchmark to evaluate solve rate across the dictionary:
```bash
python benchmark_solver.py
```

Useful options:
```bash
python benchmark_solver.py --num-seeds 10 --seed-start 0
python benchmark_solver.py --word-limit 500 --sample-failed 20
python benchmark_solver.py --json-out benchmark_results.json
```

What this does:
- Simulates full games automatically (no manual input required)
- Computes solve rate, average turns, and failed-word list
- Finds hard words across multiple random seeds
- Overwrites `notes.md` with the latest benchmark summary on every run

## Naive Solver: How It Works

The current solver is intentionally naive (heuristic, not trained).

### Core loop
1. Choose a guess from the current candidate list.
2. Receive feedback as a 5-digit code:
- `2` = green (correct letter, correct position)
- `1` = yellow (correct letter, wrong position)
- `0` = grey (not present, accounting for duplicate-letter counts)
3. Filter candidate words to only those that would produce exactly the same feedback for that guess.
4. Repeat for up to 6 turns.

### Guess policy
1. Early turns (0-1): frequency-biased probing.
2. Later turns: choose from narrowed candidates.
3. Repeated guesses are avoided.

## Image Examples
Green - Correct Position
Yellow - Wrong Position  
Grey - Not in Word

![Example1 (Opera) Yellow-Grey-Grey-Grey-Grey](https://github.com/advaithsriram/Wordle-Solver/blob/main/images/example1.png)  

In the above image, the corresponding feedback would be: Yellow-Grey-Grey-Grey-Grey

![Example2 (Those) Yellow-Yellow-Green-Grey-Grey](https://github.com/advaithsriram/Wordle-Solver/blob/main/images/example2.png)  

In the above image, the corresponding feedback would be: Yellow-Yellow-Green-Grey-Grey

## Performance
The solver typically finds the answer within 4-6 attempts, with high confidence by turn 3-4.

## License
MIT
