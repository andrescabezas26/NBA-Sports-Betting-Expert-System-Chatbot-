#!/usr/bin/env python3
"""
Debug script to see exactly what triggered_rules contains
"""

from expert_engine import BettingExpertEngine
from models import TeamStats


def main():
    print("🔍 Debugging Triggered Rules Content")
    print("=" * 50)

    # Create expert engine
    engine = BettingExpertEngine()

    # Test with a high-risk scenario
    team_stats = TeamStats(
        team_name="Test Team",
        wins=5,
        losses=25,
        win_percentage=0.17,
        points_per_game=95.0,
        opponent_points_per_game=118.0,
        home_record="3-17",
        away_record="2-8",
        last_10_games="1-9",
        streak="L5",
        unavailable_players=["LeBron James", "Anthony Davis"],
        key_players_unavailable=True,
        key_players_unavailable_count=2,
        consecutive_losses=5,
        consecutive_wins=0,
    )

    # Run analysis
    print("Running expert analysis...")
    result = engine.analyze_bet(team_stats, "away", "Strong Opponent")

    print(f"\n=== RAW TRIGGERED RULES ===")
    triggered_rules = result.get("triggered_rules", [])
    print(f"Type: {type(triggered_rules)}")
    print(f"Length: {len(triggered_rules)}")

    for i, rule in enumerate(triggered_rules):
        print(f"{i+1}. '{rule}' (type: {type(rule)})")

        # Try to extract rule name if it contains ':'
        if ":" in str(rule):
            parts = str(rule).split(":")
            print(f"    Potential rule name: '{parts[0].strip()}'")

        # Check if it contains 'rule_'
        if "rule_" in str(rule):
            # Find the rule_ part
            rule_str = str(rule)
            start = rule_str.find("rule_")
            if start != -1:
                # Extract from 'rule_' until space or end
                end = rule_str.find(" ", start)
                if end == -1:
                    rule_name = rule_str[start:]
                else:
                    rule_name = rule_str[start:end]
                print(f"    Extracted rule name: '{rule_name}'")

    print(f"\n=== OTHER RESULT FIELDS ===")
    for key, value in result.items():
        if key != "triggered_rules":
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
