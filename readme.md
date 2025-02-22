# Pybaseball Simulator - Setup and Usage Guide

## Prerequisites
Before running the Pybaseball Simulator, ensure you have Python installed on your system. This game requires Python 3.10^.

## Step 1: Install Dependencies
First, install the required Python packages:

```sh
pip install -r requirements.txt
```

## Step 2: Run the Game
Once dependencies are installed, navigate to the project directory and run the game from the src directory in your terminal:

```sh
python -m src.sim.Simulator
```

## Step 3: Configure Game Settings
When you run the game, you will be prompted to configure several options:

1. **Play-by-play output**: Choose whether to receive a detailed printout of the game (`y` for yes, `n` for no).
2. **Number of innings**: Select how many innings you want to play (1-9).
3. **Game speed**: Choose from `turtle`, `deer`, or `cheetah` for the pace of the game.
Turtle speed is for the casual observer experience with a second to fiv seconds of delay between actions.
Deer speed is moderate. And leaves a second or two of delay between actions.
Cheetah speed allows for an immediate printout of an entire game with all the delay cut out. This is optimal for experimenting with data analysis.

## Step 4: Enjoy the Game!
Watch the simulation unfold with generated teams, play-by-play commentary, and final box scores.

## Optional: Virtual Environment (Recommended)
To avoid dependency conflicts, consider using a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python -m src.sim.Simulator
```

## Troubleshooting
- If you encounter missing dependencies, check for errors and install the required package using `pip install <package_name>`.
- Ensure you are using the correct Python version (`python --version`).
- If the game does not start, verify that `Simulator.py` is in the correct directory and is executable.

Play Ball! ⚾

