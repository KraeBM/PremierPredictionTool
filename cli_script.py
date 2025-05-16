# -*- coding: utf-8 -*-
"""
ENGLISH PREMIER LEAGUE CHAMPION PREDICTION PROJECT

FINAL COMMAND LINE INTERFACE APPLICATION
"""
import os
import sys

import pandas as pd
import subprocess

#  Ensure script runs from its own directory
script_dir = os.path.dirname(os.path.abspath(__file__))

#  Path to Simulation Script & Dataset
simulation_script_path = os.path.join(script_dir, "ModelScriptsForCLI/simulation_approach.py")
# used for its individual results - providing correct simulations for prediction.
dataset_path = os.path.join(script_dir, "Datasets/premier-league-matches.csv")

#  Loads Dataset
df = pd.read_csv(dataset_path, encoding="utf-8")

#  Gets Unique Team Names
unique_teams = sorted(pd.concat([df["Home"], df["Away"]]).unique())

#  Start Application
print(
    """
    ************************************************************
    *                                                          *
    *   🚀  WELCOME TO PremierPredictor ⚽                        *
    *                                                          *
    ************************************************************
    
       🔹 Predict Premier League match outcomes
       🔹 Compare team performances
       🔹 Forecast season standings
    
       Powered by: Machine Learning, Markov Chains, and Simulation
    
    ****************************************************************
    """
)

#  User Selects Prediction Technique
model_name = input("Choose a prediction technique \n1. ML \n2. Markov Chains \n3. Simulation \n\n").strip().lower()

if model_name in ["1", "ml"]:
    print("\nMachine Learning model is under development. Stay tuned!")
    exit()

elif model_name in ["2", "markov chains"]:
    print("\nMarkov Chains model is under development. Stay tuned!")
    exit()

elif model_name in ["3", "simulation"]:
    print("\n✅ Simulation Model Selected.")

else:
    print("\n❌ Invalid selection. Please restart and choose a valid prediction technique.")
    exit()

# Prints Team List
title = "⚽ TEAM NAMES ⚽"
num_columns = 3
column_width = 25
total_width = num_columns * column_width

# prints title for team names
print("=" * total_width)
print(title.center(total_width))
print("=" * total_width)

#loops and keeps track to display all team names available
for i, team in enumerate(unique_teams, 1):
    print(f"{i:>2}. {team:<{column_width - 5}}", end="")
    if i % num_columns == 0:
        print()

print("\n" + "=" * total_width)

# User Selects Team - must be typed exactly as in the list - or if statement is run
team_name = input("\nChoose a team from the list above whose statistics you are interested in: ").strip()


if team_name not in unique_teams:
    print("\n❌ Invalid team selection. Please restart and choose a valid team.")
    exit()

print(f"\n✅ Team Selected: {team_name}")


# Function to Run Subprocess
def run_subprocess(args):
    """Runs a subprocess with proper error handling."""
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    print(result.stdout)
    if result.stderr:
        print("\n⚠️ Error:\n", result.stderr)


#  Loop to Keep Application Running
while True:
    #  Show Analysis Options
    print("\nWhat would you like to analyze for this team?")
    print("1. Does the selected team have a higher chance of winning home or away?")
    print("2. Show who the selected team is versing next and who they versed previously.")
    print("3. Put the selected team against another team and see who is most likely to win.")
    print("4. Check who the winner will be at the end of the league and who will be 3rd, 4th, etc., up to 10.")

    user_choice = input("\nEnter your choice (1-4): ").strip()

    #  Handle Each Option
    if user_choice == "1":
        print(f"\n🔍 Analyzing home vs. away performance for {team_name}...\n")
        run_subprocess([sys.executable, simulation_script_path, team_name, "home_away"])

    elif user_choice == "2":
        print(f"\n🔍 Fetching previous and upcoming matches for {team_name}...\n")
        run_subprocess([sys.executable, simulation_script_path, team_name, "matches"])

    elif user_choice == "3":
        opponent_team = input("\nEnter the name of the opponent team: ").strip()
        if opponent_team not in unique_teams:
            print("\n❌ Invalid opponent selection. Please restart and choose a valid team.")
            continue
        print(f"\n🔍 Simulating match between {team_name} and {opponent_team}...\n")
        run_subprocess([sys.executable, simulation_script_path, team_name, "head_to_head", opponent_team])

    elif user_choice == "4":
        print(f"\n🔍 Running full season simulation and predicting final standings...\n")
        run_subprocess([sys.executable, simulation_script_path, team_name, "league_standings"])

    else:
        print("\n❌ Invalid choice. Please enter a valid option (1-4).")
        continue

    #  Ask User if They Want to View More Statistics
    continue_choice = input("\nWould you like to view more statistics? (yes/no): ").strip().lower()
    if continue_choice in ["no", "n"]:
        print("\n👋 Thank you for using PremierPredict! Goodbye!\n")
        break

