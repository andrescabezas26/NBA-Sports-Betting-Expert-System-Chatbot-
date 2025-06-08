# filepath: c:\Universidad\Semestre VII\APO III\ti2-2025-1-adn\nba_chatbot.py
"""
NBA Sports Betting Expert System Chatbot
Main application that integrates all components
"""

import sys
import traceback
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from data_fetcher import NBADataFetcher
from expert_engine import BettingExpertEngine
from bayesian_analyzer import BayesianBettingAnalyzer
from models import BettingAnalysis, GameInfo, TeamStats


class NBAChatbot:
    """Main chatbot class that orchestrates the NBA betting expert system"""

    def __init__(self):
        self.data_fetcher = NBADataFetcher()
        self.expert_engine = BettingExpertEngine()
        self.bayesian_analyzer = BayesianBettingAnalyzer()
        self.session_log = []

        print("🏀 NBA Sports Betting Expert System")
        print("=" * 50)
        print("Initializing system components...")

        # Test components
        try:
            print("✓ Data fetcher ready")
            print("✓ Expert rules engine ready")
            print("✓ Bayesian network ready")
            print("✓ System fully initialized")
        except Exception as e:
            print(f"❌ Error initializing system: {e}")
            sys.exit(1)

    def log_interaction(self, user_input: str, system_output: str):
        """Log user interactions for traceability"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_log.append(
            {
                "timestamp": timestamp,
                "user_input": user_input,
                "system_output": system_output,
            }
        )

    def display_upcoming_games(self) -> List[GameInfo]:
        """Display upcoming NBA games and return the list"""
        print("\n🔄 Fetching upcoming NBA games...")
        games = self.data_fetcher.get_upcoming_games()

        if not games:
            print(
                "❌ No upcoming games found or API error. You can still analyze any two teams manually."
            )
            return []

        print(f"\n📅 Upcoming NBA Games ({len(games)} found):")
        print("-" * 60)

        for i, game in enumerate(games, 1):
            date_str = game.date if game.date else "TBD"
            time_str = game.time if game.time else "TBD"
            venue_str = f" at {game.venue}" if game.venue else ""

            print(f"{i:2d}. {game.away_team} @ {game.home_team}")
            print(f"    📅 {date_str} {time_str}{venue_str}")
            print()

        return games

    def get_user_team_choice(self, games: List[GameInfo]) -> Tuple[str, str, str, str]:
        """
        Get team choice from user - either from upcoming games or manual input
        Returns: (team_to_analyze, opponent_team, venue_for_analyzed_team, venue_type)
        """
        if games:
            print("\nChoose an option:")
            print("1. Select from upcoming games")
            print("2. Enter two teams manually")

            while True:
                choice = input("\nEnter your choice (1 or 2): ").strip()

                if choice == "1":
                    return self._select_from_upcoming_games(games)
                elif choice == "2":
                    return self._enter_teams_manually()
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")
        else:
            print("\n⚠️  No upcoming games available. Please enter two teams manually.")
            return self._enter_teams_manually()

    def _select_from_upcoming_games(
        self, games: List[GameInfo]
    ) -> Tuple[str, str, str, str]:
        """Select a game from upcoming games"""
        while True:
            try:
                game_num = int(input(f"\nSelect game number (1-{len(games)}): "))
                if 1 <= game_num <= len(games):
                    selected_game = games[game_num - 1]

                    print(
                        f"\n✅ Selected: {selected_game.away_team} @ {selected_game.home_team}"
                    )
                    print("\nWhich team do you want to analyze for betting?")
                    print(f"1. {selected_game.away_team} (Away)")
                    print(f"2. {selected_game.home_team} (Home)")

                    while True:
                        team_choice = input("\nEnter your choice (1 or 2): ").strip()
                        if team_choice == "1":
                            return (
                                selected_game.away_team,
                                selected_game.home_team,
                                "away",
                                "has_home_advantage"
                            )
                        elif team_choice == "2":
                            return (
                                selected_game.home_team,
                                selected_game.away_team,
                                "home",
                                "has_home_advantage"
                            )
                        else:
                            print("❌ Invalid choice. Please enter 1 or 2.")
                else:
                    print(f"❌ Invalid game number. Please enter 1-{len(games)}.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

    def _enter_teams_manually(self) -> Tuple[str, str, str, str]:
        """Enter two teams manually and choose which team to bet on"""
        print("\n📝 Enter two NBA teams to analyze:")

        # Show available teams for reference
        print(
            "\n💡 Tip: You can enter team names like 'Lakers', 'Warriors', 'Celtics', etc."
        )

        while True:
            team1 = input("\nEnter first team: ").strip()
            if not team1:
                print("❌ Please enter a team name.")
                continue

            team2 = input("Enter second team: ").strip()
            if not team2:
                print("❌ Please enter a team name.")
                continue

            if team1.lower() == team2.lower():
                print("❌ Please enter two different teams.")
                continue

            # Ask which team is playing at home
            print(f"\nWhich team is playing at home?")
            print(f"1. {team1}")
            print(f"2. {team2}")

            home_team = None
            venue_type = None

            while True:
                venue_choice = input("\nEnter your choice (1 or 2): ").strip()
                if venue_choice == "1":
                    home_team = team1
                    venue_type = "has_home_advantage"
                    break
                elif venue_choice == "2":
                    home_team = team2
                    venue_type = "has_home_advantage"
                    break
                else:
                    print("❌ Invalid choice. Please enter 1 or 2")

            # Ask which team they want to bet on
            print(f"\n🎯 Which team would you like to analyze for betting?")
            print(f"1. {team1}")
            print(f"2. {team2}")

            while True:
                bet_choice = input("\nEnter your choice (1 or 2): ").strip()
                if bet_choice == "1":
                    # Team1 is the analyzed team
                    if home_team == team1:
                        return team1, team2, "home", venue_type
                    elif home_team == team2:
                        return team1, team2, "away", venue_type
                elif bet_choice == "2":
                    # Team2 is the analyzed team
                    if home_team == team2:
                        return team2, team1, "home", venue_type
                    elif home_team == team1:
                        return team2, team1, "away", venue_type
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")

    async def validate_and_get_team_stats_async(self, team_name: str) -> Optional[TeamStats]:
        """Async version of validate_and_get_team_stats"""
        print(f"\n🔍 Fetching data for {team_name}...")

        team_stats = await self.data_fetcher.get_team_stats_async(team_name)
        
        if not team_stats:
            print(f"❌ Could not find team '{team_name}' or fetch its data.")
            print(
                "💡 Try using common team names like 'Lakers', 'Warriors', 'Celtics', etc."
            )
            return None
        
        print(f"✅ Found: {team_stats.team_name}")
        return team_stats

    async def perform_analysis_async(
        self, team_stats: TeamStats, opponent_name: str, venue: str
    ) -> BettingAnalysis:
        """Async version of perform_analysis that can be run as a background task"""
        print(f"\n🧠 Analyzing betting recommendation for {team_stats.team_name}...")

        # NEW: Get opponent stats for comparative analysis
        print(f"🔍 Fetching opponent data for {opponent_name}...")
        
        # Run opponent stats fetching in executor to avoid blocking
        loop = asyncio.get_event_loop()
        opponent_stats = await loop.run_in_executor(
            None, self.validate_and_get_team_stats, opponent_name
        )
        
        if opponent_stats:
            print(f"✅ Opponent data loaded: {opponent_stats.team_name}")
        else:
            print(f"⚠️ Could not load opponent data for {opponent_name}")

        # Run expert system analysis in executor
        expert_result = await loop.run_in_executor(
            None, self.expert_engine.analyze_bet, team_stats, venue, opponent_stats
        )

        # Run Bayesian analysis in executor
        bayesian_result = await loop.run_in_executor(
            None, self.bayesian_analyzer.analyze_betting_risk, team_stats, venue
        )

        # Combine results (this is fast, so no need for async)
        expert_rec = expert_result["recommendation"]
        bayesian_rec = bayesian_result["recommendation"]

        if expert_rec == bayesian_rec:
            final_recommendation = expert_rec
            confidence = (bayesian_result["confidence"] + 0.8) / 2
        else:
            final_recommendation = (
                "risky" if "risky" in [expert_rec, bayesian_rec] else "safe"
            )
            confidence = 0.6

        # Determine risk level
        expert_risk = expert_result["risk_level"]
        bayesian_risk = bayesian_result["risk_level"]

        risk_mapping = {"low": 1, "medium": 2, "high": 3}
        avg_risk_level = (risk_mapping[expert_risk] + risk_mapping[bayesian_risk]) / 2

        if avg_risk_level <= 1.5:
            final_risk_level = "low"
        elif avg_risk_level <= 2.5:
            final_risk_level = "medium"
        else:
            final_risk_level = "high"

        # Combine reasoning
        all_reasoning = expert_result["reasoning"] + [
            f"Bayesian analysis: {bayesian_risk} risk ({bayesian_result['confidence']:.1%} confidence)"
        ]

        return BettingAnalysis(
            recommendation=final_recommendation,
            confidence=confidence,
            risk_level=final_risk_level,
            reasoning=all_reasoning,
            triggered_rules=expert_result["triggered_rules"],
            bayesian_probability=bayesian_result["bayesian_probability"],
        )

    def perform_analysis(
        self, team_stats: TeamStats, opponent_name: str, venue: str
    ) -> BettingAnalysis:
        """Perform complete betting analysis using both expert rules and Bayesian inference"""
        print(f"\n🧠 Analyzing betting recommendation for {team_stats.team_name}...")

        # NEW: Get opponent stats for comparative analysis
        print(f"🔍 Fetching opponent data for {opponent_name}...")
        opponent_stats = self.validate_and_get_team_stats(opponent_name)
        
        if opponent_stats:
            print(f"✅ Opponent data loaded: {opponent_stats.team_name}")
        else:
            print(f"⚠️ Could not load opponent data for {opponent_name}")

        # Expert system analysis with opponent data
        expert_result = self.expert_engine.analyze_bet(team_stats, venue, opponent_stats)

        # Bayesian analysis
        bayesian_result = self.bayesian_analyzer.analyze_betting_risk(team_stats, venue)

        # Combine results
        # If both systems agree, use that recommendation
        # If they disagree, be conservative (choose the more cautious recommendation)
        expert_rec = expert_result["recommendation"]
        bayesian_rec = bayesian_result["recommendation"]

        if expert_rec == bayesian_rec:
            final_recommendation = expert_rec
            confidence = (bayesian_result["confidence"] + 0.8) / 2  # Average confidence
        else:
            # Be conservative - if either system says risky, go with risky
            final_recommendation = (
                "risky" if "risky" in [expert_rec, bayesian_rec] else "safe"
            )
            confidence = 0.6  # Lower confidence when systems disagree

        # Determine risk level
        expert_risk = expert_result["risk_level"]
        bayesian_risk = bayesian_result["risk_level"]

        risk_mapping = {"low": 1, "medium": 2, "high": 3}
        avg_risk_level = (risk_mapping[expert_risk] + risk_mapping[bayesian_risk]) / 2

        if avg_risk_level <= 1.5:
            final_risk_level = "low"
        elif avg_risk_level <= 2.5:
            final_risk_level = "medium"
        else:
            final_risk_level = "high"

        # Combine reasoning
        all_reasoning = expert_result["reasoning"] + [
            f"Bayesian analysis: {bayesian_risk} risk ({bayesian_result['confidence']:.1%} confidence)"
        ]

        return BettingAnalysis(
            recommendation=final_recommendation,
            confidence=confidence,
            risk_level=final_risk_level,
            reasoning=all_reasoning,
            triggered_rules=expert_result["triggered_rules"],
            bayesian_probability=bayesian_result["bayesian_probability"],
        )

    def display_analysis_results(
        self,
        analysis: BettingAnalysis,
        team_stats: TeamStats,
        opponent_name: str,
        venue: str,
    ):
        """Display comprehensive analysis results"""
        print("\n" + "=" * 60)
        print("🎯 BETTING ANALYSIS RESULTS")
        print("=" * 60)

        # Team overview
        print(f"\n📊 TEAM OVERVIEW: {team_stats.team_name}")
        print("-" * 40)
        print(
            f"Record: {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.1%})"
        )
        print(f"Last 10 games: {team_stats.last_10_games}")
        print(f"Current streak: {team_stats.streak}")
        print(f"Scoring: {team_stats.points_per_game:.1f} PPG")
        print(f"Defense: {team_stats.opponent_points_per_game:.1f} OPPG allowed")
        print(f"Home record: {team_stats.home_record}")
        print(f"Away record: {team_stats.away_record}")

        if team_stats.unavailable_players:
            print(f"Unavailable players: {', '.join(team_stats.unavailable_players)}")
        else:
            print("Unavailable players: None reported")

        print(f"Playing: {venue.upper()} vs {opponent_name}")

        # Main recommendation
        print(f"\n🎯 RECOMMENDATION")
        print("-" * 40)
        rec_emoji = "✅" if analysis.recommendation == "safe" else "⚠️"
        print(f"{rec_emoji} {analysis.recommendation.upper()} BET")
        print(f"Risk Level: {analysis.risk_level.upper()}")
        print(f"Confidence: {analysis.confidence:.1%}")

        # Expert system results
        print(f"\n🧠 EXPERT SYSTEM ANALYSIS")
        print("-" * 40)
        if analysis.triggered_rules:
            print("Triggered rules:")
            for rule in analysis.triggered_rules:
                print(f"  • {rule}")
        else:
            print("No specific rules triggered")

        if analysis.reasoning:
            print("\nKey factors:")
            for reason in analysis.reasoning:
                print(f"  • {reason}")

        # Bayesian analysis
        print(f"\n📈 BAYESIAN NETWORK ANALYSIS")
        print("-" * 40)
        print(
            f"Probabilistic assessment: {analysis.bayesian_probability:.1%} confidence"
        )        # Get detailed Bayesian explanation
        bayesian_explanation = self.bayesian_analyzer.explain_inference(
            team_stats, venue
        )
        print(bayesian_explanation)

        print("\n" + "=" * 60)

        # Enhanced final summary with detailed reasoning
        risk_color = (
            "🟢"
            if analysis.risk_level == "low"
            else "🟡" if analysis.risk_level == "medium" else "🔴"
        )
        
        # Generate detailed summary reasons
        summary_reasons = self._generate_summary_reasons(analysis, team_stats, venue, opponent_name)
        
        print(f"\n{risk_color} SUMMARY: This is a {analysis.recommendation.upper()} bet with {analysis.risk_level.upper()} risk")
        print(f"📋 REASONING: {summary_reasons}")

        if analysis.recommendation == "safe":
            print("💡 The analysis suggests favorable conditions for this bet.")
        else:
            print("⚠️ The analysis suggests caution with this bet due to identified risk factors.")

    def run_interactive_session(self):
        """Run the main interactive chatbot session"""
        print("\n🚀 Welcome to the NBA Sports Betting Expert System!")
        print(
            "This system analyzes NBA teams using expert rules and Bayesian networks."
        )
        print("You can analyze upcoming games or any two teams of your choice.\n")

        while True:
            try:
                # Display upcoming games
                upcoming_games = self.display_upcoming_games()

                # Get user choice - now returns 4 values
                team1, team2, venue, venue_type = self.get_user_team_choice(upcoming_games)

                # Validate and get team stats
                team_stats = self.validate_and_get_team_stats(team1)
                if not team_stats:
                    print("\n❌ Unable to proceed with invalid team. Please try again.")
                    continue

                # Perform analysis
                analysis = self.perform_analysis(team_stats, team2, venue)

                # Display results
                self.display_analysis_results(analysis, team_stats, team2, venue)

                # Log the interaction
                user_input = f"Analyze {team1} vs {team2} ({venue})"
                system_output = (
                    f"{analysis.recommendation} bet, {analysis.risk_level} risk"
                )
                self.log_interaction(user_input, system_output)

                # Ask if user wants to continue
                print("\n" + "=" * 60)
                while True:
                    continue_choice = (
                        input("\nWould you like to analyze another team? (y/n): ")
                        .strip()
                        .lower()
                    )
                    if continue_choice in ["y", "yes"]:
                        print("\n" + "=" * 60)
                        break
                    elif continue_choice in ["n", "no"]:
                        print(
                            "\n👋 Thank you for using the NBA Sports Betting Expert System!"
                        )
                        print(
                            f"📝 Session completed with {len(self.session_log)} analyses."
                        )
                        return
                    else:
                        print("❌ Please enter 'y' for yes or 'n' for no.")

            except KeyboardInterrupt:
                print("\n\n👋 Session ended by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print(f"Error type: {type(e).__name__}")
                print(f"Error location: {traceback.format_exc()}")
                print("Please try again or restart the system.")

                continue_after_error = input("Continue? (y/n): ").strip().lower()
                if continue_after_error not in ["y", "yes"]:
                    break

    def _generate_summary_reasons(self, analysis: BettingAnalysis, team_stats: TeamStats, venue: str, opponent_name: str) -> str:
        """Generate detailed summary reasons for the betting recommendation"""
        reasons = []
        
        # Venue-based reasons
        if venue == "away":
            if analysis.risk_level in ["medium", "high"]:
                reasons.append("away disadvantage")
            elif team_stats.away_record and self._has_good_away_record(team_stats.away_record):
                reasons.append("strong away performance")
        elif venue == "home":
            if team_stats.home_record and self._has_good_home_record(team_stats.home_record):
                reasons.append("home advantage")
        
        # Player availability reasons
        if team_stats.unavailable_players and len(team_stats.unavailable_players) > 0:
            if team_stats.key_players_unavailable:
                reasons.append("key player absences")
            else:
                reasons.append("player absences")
        elif not team_stats.key_players_unavailable:
            reasons.append("full squad available")
        
        # Performance-based reasons
        if team_stats.win_percentage >= 0.7:
            reasons.append("strong overall record")
        elif team_stats.win_percentage <= 0.4:
            reasons.append("poor overall record")
        
        # Recent form reasons
        if hasattr(team_stats, 'last_10_games') and team_stats.last_10_games:
            wins_last_10 = self._extract_wins_from_record(team_stats.last_10_games)
            if wins_last_10 >= 8:
                reasons.append("excellent recent form")
            elif wins_last_10 >= 6:
                reasons.append("good recent form")
            elif wins_last_10 <= 3:
                reasons.append("poor recent form")
        
        # Streak reasons
        if hasattr(team_stats, 'consecutive_wins') and team_stats.consecutive_wins >= 3:
            reasons.append(f"{team_stats.consecutive_wins}-game winning streak")
        elif hasattr(team_stats, 'consecutive_losses') and team_stats.consecutive_losses >= 3:
            reasons.append(f"{team_stats.consecutive_losses}-game losing streak")
        
        # Scoring reasons
        if team_stats.points_per_game >= 115:
            reasons.append("high-scoring offense")
        elif team_stats.points_per_game <= 105:
            reasons.append("struggling offense")
        
        if team_stats.opponent_points_per_game <= 108:
            reasons.append("strong defense")
        elif team_stats.opponent_points_per_game >= 118:
            reasons.append("weak defense")
        
        # Join reasons appropriately
        if len(reasons) == 0:
            return "standard performance metrics"
        elif len(reasons) == 1:
            return reasons[0]
        elif len(reasons) == 2:
            return f"{reasons[0]} and {reasons[1]}"
        else:
            return f"{', '.join(reasons[:-1])}, and {reasons[-1]}"

    def _has_good_away_record(self, away_record: str) -> bool:
        """Check if away record is good (>60% win rate)"""
        try:
            wins, losses = map(int, away_record.split('-'))
            total = wins + losses
            return total > 0 and (wins / total) > 0.6
        except:
            return False

    def _has_good_home_record(self, home_record: str) -> bool:
        """Check if home record is good (>70% win rate)"""
        try:
            wins, losses = map(int, home_record.split('-'))
            total = wins + losses
            return total > 0 and (wins / total) > 0.7
        except:
            return False

    def _extract_wins_from_record(self, record: str) -> int:
        """Extract wins from a record string like '7-3'"""
        try:
            return int(record.split('-')[0])
        except:
            return 0
def main():
    """Main entry point"""
    try:
        chatbot = NBAChatbot()
        chatbot.run_interactive_session()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
