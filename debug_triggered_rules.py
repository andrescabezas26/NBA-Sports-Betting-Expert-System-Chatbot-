#!/usr/bin/env python3
"""
Debug test to see what triggered_rules actually contains
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import NBADataFetcher
from expert_engine import BettingExpertEngine
from models import TeamStats


def debug_triggered_rules():
    """Debug what triggered_rules contains"""
    print("🔍 Debugging Triggered Rules")
    print("=" * 40)

    # Create expert engine
    expert_engine = BettingExpertEngine()

    # Create a test scenario that should trigger rules
    team_stats = TeamStats(
        team_name="Test Team",
        wins=8,
        losses=32,
        streak="L5",
        win_percentage=0.25,
        consecutive_wins=0,
        consecutive_losses=5,
        points_per_game=95.0,
        opponent_points_per_game=118.0,
        last_10_games="2-8",
        last_5_games="0-5",
        home_record="5-15",
        away_record="3-17",
        key_players_unavailable=True,
        unavailable_players=["Player A", "Player B", "Player C"],
        key_players_unavailable_count=3,
        back_to_back=True,
        rest_days=0,
    )

    print(f"Testing with team: {team_stats.team_name}")
    print(f"Win percentage: {team_stats.win_percentage}")
    print(f"Consecutive losses: {team_stats.consecutive_losses}")
    print(f"Key players unavailable: {team_stats.key_players_unavailable}")
    print(f"Back to back: {team_stats.back_to_back}")
    print()

    # Run analysis
    result = expert_engine.analyze_bet(team_stats, "away", "Strong Opponent")

    print("Expert Engine Results:")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Risk level: {result['risk_level']}")
    print(f"Number of triggered rules: {len(result['triggered_rules'])}")
    print()

    print("Triggered Rules Details:")
    for i, rule in enumerate(result["triggered_rules"], 1):
        print(f"{i:2d}. {rule}")

    print()
    print("Risk Factors:")
    for i, factor in enumerate(result["risk_factors"], 1):
        print(f"{i:2d}. {factor}")

    print()
    print("Safe Factors:")
    for i, factor in enumerate(result["safe_factors"], 1):
        print(f"{i:2d}. {factor}")


if __name__ == "__main__":
    debug_triggered_rules()
