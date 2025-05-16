# -*- coding: utf-8 -*-
"""
ENGLISH PREMIER LEAGUE CHAMPION PREDICTION PROJECT - SIMULATION APPROACH
"""

import os
import sys
import numpy as np
import pandas as pd
import random

# Ensures script runs from its own directory
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "../Datasets/Premier_League_Standings.csv")
matches_path = os.path.join(script_dir, "../Datasets/premier-league-matches.csv")

# Loads Dataset (Force UTF-8 Encoding)
data = pd.read_csv(data_path, encoding="utf-8")

# Computes Historical Performance by Giving much higher importance to last 5 years
# e.g. 2018 = 1 + (2018-2015)/5 = 1.6 (more important that 2015 which was 1)
data["SeasonWeight"] = data["Season"].apply(lambda x: 1 if x < 2015 else (1 + (x - 2015) / 5))

# Computes weighted team performance
team_performance = data.groupby("Team", group_keys=False).apply(lambda x: pd.Series({
    "Weighted_Pts": np.average(x["Pts"], weights=x["SeasonWeight"]),
    "GF": np.average(x["GF"], weights=x["SeasonWeight"]),
    "GA": np.average(x["GA"], weights=x["SeasonWeight"]),
    "GD": np.average(x["GD"], weights=x["SeasonWeight"]),
    "W": np.average(x["W"], weights=x["SeasonWeight"]),
    "D": np.average(x["D"], weights=x["SeasonWeight"]),
    "L": np.average(x["L"], weights=x["SeasonWeight"]),
    "Pld": np.average(x["Pld"], weights=x["SeasonWeight"])
})).reset_index()

#  ensures Necessary Columns Exist and also calculates the teams Strength, Weakness and Win rate
if "GF" in team_performance and "Pld" in team_performance:
    team_performance["Attack_Strength"] = team_performance["GF"] / team_performance["Pld"]
    team_performance["Defense_Strength"] = team_performance["GA"] / team_performance["Pld"]
    team_performance["Win_Rate"] = team_performance["W"] / team_performance["Pld"]
else:
    print("\n❌ ERROR: Columns `GF` or `Pld` missing in dataset!")

# Converts into dictionary for fast lookup for later
team_stats_dict = team_performance.set_index("Team")[["Attack_Strength", "Defense_Strength", "Win_Rate"]].to_dict(orient="index")

# Function which simulates Match Outcome
def simulate_match(home_team, away_team):
    """Simulates a match outcome using attack/defense strength of teams."""
    if home_team not in team_stats_dict or away_team not in team_stats_dict:
        return np.random.choice(["H", "D", "A"], p=[1/3, 1/3, 1/3])  # No data = fair randomised probability of winning.#
                                                                        # Each outcome has a 1/3 of winning #
    #Due to introduction of team versing, removing -/+ 5% prevents instability of prediction for every game + improves interpretation
    # Other version in GOOGLE COLLAB was better for understanding strength of predictability (MAE) and better analysis
    home_attack = team_stats_dict[home_team]["Attack_Strength"]
    away_attack = team_stats_dict[away_team]["Attack_Strength"]
    home_defense = team_stats_dict[home_team]["Defense_Strength"]
    away_defense = team_stats_dict[away_team]["Defense_Strength"]

    home_advantage = (home_attack + away_defense) - (away_attack + home_defense)

    if home_advantage > 0.2:
        return "H"
    elif home_advantage < -0.2:
        return "A"
    return "D"

# This fucntion determines Home vs. Away Performance - comparing their strengths
def analyze_home_away(team_name):
    """Analyzes whether the team performs better at home or away."""
    team_stats = team_stats_dict.get(team_name)

    if not team_stats:
        print(f"❌ Team data not found for {team_name}")
        return

    home_advantage = team_stats["Attack_Strength"] - team_stats["Defense_Strength"]

    if home_advantage > 0:
        print(f"\n🏠 {team_name} has a higher chance of winning at **HOME**")
    else:
        print(f"\n🚗 {team_name} has a higher chance of winning **AWAY**")


# This fucntion is made to show previous & predicted future matches
def show_matches(team_name):
    """Displays past matches and predicts future match outcomes based on historical data."""
    df = pd.read_csv(matches_path, encoding="utf-8")

    if "HomeGoals" in df and "AwayGoals" in df:
        goal_columns = ["HomeGoals", "AwayGoals"]
    else:
        print("\n❌ ERROR: Expected columns 'HomeGoals' and 'AwayGoals' not found in dataset!")
        return

    team_matches = df[(df["Home"] == team_name) | (df["Away"] == team_name)][["Date", "Home", "Away"] + goal_columns]
    # Last 5 completed matches
    past_matches = team_matches.dropna().tail(5)
    print(f"\n📅 **Last 5 Matches for {team_name}:**\n")
    print(past_matches.to_string(index=False))

    # Predicts Next 5 Matches
    possible_opponents = df["Home"].unique()
    possible_opponents = [team for team in possible_opponents if team != team_name]
    future_opponents = random.sample(possible_opponents, 5)

    predictions = []
    for opponent in future_opponents:
        result = simulate_match(team_name, opponent)
        predictions.append((team_name, opponent, result))

    print(f"\n📊 **Predicted Next 5 Matches for {team_name}:**\n")
    print(f"{'Home Team':<20} {'Away Team':<20} {'Predicted Result':<20}")
    print("=" * 60)
    for home, away, outcome in predictions:
        result_text = "🏆 Home Win" if outcome == "H" else "⚖️ Draw" if outcome == "D" else "🚀 Away Win"
        print(f"{home:<20} {away:<20} {result_text:<20}")

# This function simulates Full Season Standings
def simulate_season(team_name):
    """Simulates an entire Premier League season and checks if the selected team is in the top 10."""
    latest_season = data["Season"].max()
    valid_teams = data[data["Season"] == latest_season]["Team"].tolist()
    historical_teams = [team for team in team_performance["Team"] if team in valid_teams]

    num_simulations = 1000
    final_rankings = {team: [] for team in historical_teams}

    for _ in range(num_simulations):
        standings = {team: 0 for team in historical_teams}

        # Simulates matches between teams
        for home_team in historical_teams:
            for away_team in historical_teams:
                if home_team != away_team:
                    result = simulate_match(home_team, away_team)
                    if result == "H":
                        standings[home_team] += 3
                    elif result == "D":
                        standings[home_team] += 1
                        standings[away_team] += 1
                    else:
                        standings[away_team] += 3

        # Store final position of each team in rankings
        sorted_teams = sorted(standings.items(), key=lambda x: x[1], reverse=True)
        for rank, (team, points) in enumerate(sorted_teams):
            final_rankings[team].append(rank + 1)

    # Create a DataFrame with average positions
    final_rankings_df = pd.DataFrame({team: np.mean(ranks) for team, ranks in final_rankings.items()},
                                     index=["Avg Position"]).T
    final_rankings_df = final_rankings_df.sort_values(by="Avg Position").head(10)

    # Print the top 10 teams
    print("\n🏆 **Predicted Premier League Standings:**\n")
    print(final_rankings_df.round(2).to_string())

    # Check if selected team is in top 10
    if team_name not in final_rankings_df.index:
        print(f"\n⚠️ {team_name} is not in the top 10.")

# This function simulates the match between 2 chosen teams
def simulate_head_to_head(team1, team2):
    """Simulates a match between two teams and predicts the winner using strength-based probabilities."""
    if team1 not in team_stats_dict or team2 not in team_stats_dict:
        print("\n❌ One or both teams do not exist in the dataset.")
        return

    # Calculate strengths
    team1_strength = team_stats_dict[team1]["Attack_Strength"] - team_stats_dict[team2]["Defense_Strength"]
    team2_strength = team_stats_dict[team2]["Attack_Strength"] - team_stats_dict[team1]["Defense_Strength"]

    print(f"\n Head-to-Head Prediction: {team1} vs {team2}")
    print(f"   ⚡ {team1} Strength: {team1_strength:.2f}")
    print(f"   ⚡ {team2} Strength: {team2_strength:.2f}")

    # Normalize strengths to create valid probabilities
    total_strength = abs(team1_strength) + abs(team2_strength)
    if total_strength == 0:
        total_strength = 0.01  # Avoid division by zero

    team1_prob = abs(team1_strength) / total_strength
    team2_prob = abs(team2_strength) / total_strength
    draw_prob = max(1 - (team1_prob + team2_prob), 0.2)  # Ensure non-zero draw probability

    # Normalize to make sure they sum to 1
    total_prob = team1_prob + team2_prob + draw_prob
    team1_prob /= total_prob
    team2_prob /= total_prob
    draw_prob /= total_prob

    # Simulate match result
    result = np.random.choice(["H", "D", "A"], p=[team1_prob, draw_prob, team2_prob])

    # Print final result
    if result == "H":
        print(f"\n🏆 **{team1} is more likely to win!**")
    elif result == "D":
        print(f"\n⚖️ **The match between {team1} and {team2} is likely to end in a DRAW.**")
    else:
        print(f"\n🏆 **{team2} is more likely to win!**")

# Execution Block  - This ensure this runs only when called from CLI
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ No team or analysis option provided. Please provide both as arguments.")
        sys.exit(1)

    team_name = sys.argv[1]
    analysis_type = sys.argv[2]

    print(f"\n🎮 Running Analysis for: {team_name} ({analysis_type})...\n")

    if analysis_type == "home_away":
        analyze_home_away(team_name)
    elif analysis_type == "matches":
        show_matches(team_name)
    elif analysis_type == "head_to_head":
        if len(sys.argv) < 4:
            print("\n❌ No opponent provided for head-to-head analysis.")
            sys.exit(1)
        opponent_team = sys.argv[3]
        simulate_head_to_head(team_name, opponent_team)  # Now correctly calls the function
    elif analysis_type == "league_standings":
        simulate_season(team_name)
    else:
        print("\n❌ Invalid analysis option. Please restart and enter a valid option.")
