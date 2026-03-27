# Wordle-Solver
A Python program that can solve the daily NY Times' Wordle using AI and letter frequency analysis.

## Features
- AI-powered word guessing using letter frequency analysis
- Interactive Streamlit web UI with color-coded feedback
- Real-time confidence tracking and word possibility updates

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

## How It Works

The solver uses a strategic approach:
1. **Letter Frequency Analysis**: Analyzes which letters appear most frequently in the valid word list
2. **Elimination**: Removes words that don't match your feedback
3. **Dynamic Strategy**: Adjusts its guessing strategy based on confidence and remaining possibilities
4. **Continuous Learning**: If no valid words remain, you can submit the actual word to help improve the database

## Deploying to Cloud

### Deploy on Streamlit Cloud (Easiest)
1. Push your repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your GitHub repository, branch, and specify `wordle_ui.py` as the main file
5. Click "Deploy"

### Deploy on Heroku
1. Create a `Procfile` in your project root:
```
web: streamlit run wordle_ui.py --logger.level=error
```

2. Create a `.streamlit/config.toml` file:
```toml
[server]
headless = true
port = $PORT
enableCORS = false
```

3. Deploy using Heroku CLI:
```bash
git push heroku main
```

### Deploy on AWS / Other Cloud Providers
Streamlit can be deployed on any platform that supports Python. Follow Streamlit's [deployment documentation](https://docs.streamlit.io/streamlit-cloud/deploy-your-app) for detailed instructions.

## Example Gameplay

1. The AI suggests a word (e.g., "STARE")
2. You play it in Wordle and see the color feedback
3. Click the corresponding color button for each letter in the suggested word
4. Click "Enter"
5. The AI narrows down possibilities and suggests your next word
6. Repeat until solved!

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
See LICENSE file for details
