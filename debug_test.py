#!/usr/bin/env python3
"""
Debug script to isolate the 'self' error
"""

from models import TeamStats
from expert_engine import BettingExpertEngine

# Create test data
test_stats = TeamStats(
    team_name="Test Team",
    wins=10,
    losses=5,
    win_percentage=0.67,
    points_per_game=110.5,
    opponent_points_per_game=105.2,
    home_record="6-2",
    away_record="4-3",
    last_10_games="7-3",
    streak="W2",
    unavailable_players=["Player A (knee)"],
    key_players_unavailable=True,
    consecutive_losses=0,
    consecutive_wins=2,
)

print("Creating expert engine...")
try:
    engine = BettingExpertEngine()
    print("✓ Expert engine created successfully")
except Exception as e:
    print(f"❌ Error creating expert engine: {e}")
    import traceback

    traceback.print_exc()
    exit(1)

print("Testing analysis...")
try:
    result = engine.analyze_bet(test_stats, "home")
    print("✓ Analysis completed successfully")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback

    traceback.print_exc()

print("\nTesting with venue 'away'...")
try:
    result = engine.analyze_bet(test_stats, "away")
    print("✓ Analysis completed successfully")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback

    traceback.print_exc()
