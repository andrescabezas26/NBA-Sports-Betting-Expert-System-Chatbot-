"""
Expert Rules Engine
Implements expert system rules using Experta for NBA betting analysis
"""

from experta import KnowledgeEngine, Rule, DefFacts, Fact, AS, P, L, W
from models import (
    TeamFact,
    GameFact,
    AvailabilityFact,
    PerformanceFact,
    VenueFact,
    BettingRecommendation,
    TeamStats,
    OpponentFact,
    OpponentPerformanceFact,
    OpponentAvailabilityFact,
    MatchupFact,
)
from typing import List, Dict, Any


class BettingExpertEngine(KnowledgeEngine):
    """Expert system for NBA betting recommendations"""

    def __init__(self):
        super().__init__()
        self.triggered_rules = []
        self.risk_factors = []
        self.safe_factors = []
        self.betting_recommendations = []  # Add this to store recommendations

    def reset_analysis(self):
        """Reset analysis for new evaluation"""
        self.triggered_rules = []
        self.risk_factors = []
        self.safe_factors = []
        self.betting_recommendations = []  # Reset recommendations too

    @DefFacts()
    def initial_facts(self):
        """Define initial facts"""
        yield Fact(system="NBA Betting Expert")

    # High Risk Rules
    @Rule(
        PerformanceFact(consecutive_losses=P(lambda x: x >= 3)),
        AvailabilityFact(key_players_unavailable=True),
        salience=100,
    )
    def rule_high_risk_losing_streak_with_unavailable_key_players(self):
        """High risk: Team has 3+ consecutive losses AND key players unavailable"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Team has 3+ consecutive losses with key/star players unavailable",
        )

        self.declare(betting_rec)

        # Store in our own list for retrieval
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Team has 3+ consecutive losses with key/star players unavailable",
            }
        )

        self.triggered_rules.append(
            "High Risk: Losing streak + key players unavailable"
        )
        self.risk_factors.append(
            "3+ consecutive losses with key/star players unavailable"
        )

    @Rule(
        AvailabilityFact(key_players_unavailable=True),
        PerformanceFact(win_percentage=P(lambda x: x < 0.5)),
        salience=95,
    )
    def rule_high_risk_key_players_out_struggling_team(self):
        """High risk: Key players unavailable on struggling team"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Key/star players unavailable on struggling team (win% < 50%)",
        )

        self.declare(betting_rec)

        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Key/star players unavailable on struggling team (win% < 50%)",
            }
        )

        self.triggered_rules.append("High Risk: Key players out + struggling team")
        self.risk_factors.append("Key/star players unavailable on struggling team")

    @Rule(
        AvailabilityFact(key_players_count=P(lambda x: x >= 2)),
        salience=95,
    )
    def rule_very_high_risk_multiple_key_players_out(self):
        """Very high risk: Multiple key players unavailable"""
        betting_rec = BettingRecommendation(
            risk_level="very_high",
            reason="Multiple key/star players unavailable (depth concerns)",
        )

        self.declare(betting_rec)

        self.betting_recommendations.append(
            {
                "risk_level": "very_high",
                "reason": "Multiple key/star players unavailable (depth concerns)",
            }
        )

        self.triggered_rules.append("Very High Risk: Multiple key players out")
        self.risk_factors.append(
            "Multiple key/star players unavailable - depth concerns"
        )

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x < 0.3)),
        VenueFact(venue="away"),
        salience=90,
    )
    def rule_high_risk_poor_team_away(self):
        """High risk: Poor performing team playing away"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Poor performing team (win% < 30%) playing away",
        )

        self.declare(betting_rec)

        # Store in our own list for retrieval
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Poor performing team (win% < 30%) playing away",
            }
        )

        self.triggered_rules.append("High Risk: Poor team away")
        self.risk_factors.append("Poor team performance playing away")

    @Rule(PerformanceFact(consecutive_losses=P(lambda x: x >= 5)), salience=95)
    def rule_very_high_risk_long_losing_streak(self):
        """Very high risk: Team has 5+ consecutive losses"""
        betting_rec = BettingRecommendation(
            risk_level="very_high", reason="Team has 5+ consecutive losses"
        )

        self.declare(betting_rec)

        # Store in our own list for retrieval
        self.betting_recommendations.append(
            {"risk_level": "very_high", "reason": "Team has 5+ consecutive losses"}
        )

        self.triggered_rules.append("Very High Risk: Extended losing streak")
        self.risk_factors.append("5+ consecutive losses")

    @Rule(
        PerformanceFact(points_per_game=P(lambda x: x < 105)),
        PerformanceFact(opponent_points_per_game=P(lambda x: x > 115)),
        salience=85,
    )
    def rule_high_risk_poor_offense_defense(self):
        """High risk: Poor offense and defense"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Poor offense (<105 PPG) and defense (>115 OPPG)",
        )

        self.declare(betting_rec)

        # Store in our own list for retrieval
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Poor offense (<105 PPG) and defense (>115 OPPG)",
            }
        )

        self.triggered_rules.append("High Risk: Poor offense and defense")
        self.risk_factors.append("Weak offense and defense")

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x < 0.45)),
        AvailabilityFact(key_players_count=P(lambda x: x >= 1)),
        salience=85,
    )
    def rule_high_risk_struggling_team_key_player_out(self):
        """High risk: Struggling team with key player unavailable"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Struggling team (win% < 45%) with key/star player unavailable",
        )

        self.declare(betting_rec)

        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Struggling team (win% < 45%) with key/star player unavailable",
            }
        )

        self.triggered_rules.append("High Risk: Struggling team + key player out")
        self.risk_factors.append("Below .500 team missing key/star player")

    # NEW CRITICAL RULES - FACTIBLE WITH NBA API

    @Rule(
        Fact(back_to_back=True),
        VenueFact(venue="away"),
        salience=85,
    )
    def rule_high_risk_back_to_back_away(self):
        """High risk: Back-to-back away game (fatigue factor)"""
        betting_rec = BettingRecommendation(
            risk_level="high", reason="Back-to-back games on the road (fatigue factor)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Back-to-back games on the road (fatigue factor)",
            }
        )
        self.triggered_rules.append("High Risk: B2B road game")
        self.risk_factors.append("Team playing consecutive games away")

    @Rule(
        Fact(point_differential=P(lambda x: x < -8)),
        salience=80,
    )
    def rule_high_risk_terrible_point_differential(self):
        """High risk: Team with terrible point differential"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Terrible point differential (losing by 8+ per game)",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Terrible point differential (losing by 8+ per game)",
            }
        )
        self.triggered_rules.append("High Risk: Poor scoring margin")
        self.risk_factors.append("Consistently outscored by large margin")

    @Rule(
        VenueFact(venue="away"),
        PerformanceFact(
            away_record=P(lambda x: BettingExpertEngine._is_terrible_road_record(x))
        ),
        salience=75,
    )
    def rule_high_risk_terrible_road_team(self):
        """High risk: Historically terrible road team"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Historically poor road performance (road win% < 25%)",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "high",
                "reason": "Historically poor road performance (road win% < 25%)",
            }
        )
        self.triggered_rules.append("High Risk: Terrible road team")
        self.risk_factors.append("Extremely poor away record")

    @Rule(
        Fact(back_to_back=True),
        PerformanceFact(win_percentage=P(lambda x: x < 0.5)),
        salience=75,
    )
    def rule_medium_risk_back_to_back_struggling(self):
        """Medium risk: Back-to-back for struggling team"""
        betting_rec = BettingRecommendation(
            risk_level="medium",
            reason="Back-to-back games for struggling team (fatigue impact)",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "medium",
                "reason": "Back-to-back games for struggling team (fatigue impact)",
            }
        )
        self.triggered_rules.append("Medium Risk: B2B struggling team")
        self.risk_factors.append("Fatigue factor for below .500 team")

    @Rule(
        Fact(rest_days=P(lambda x: x >= 4)),
        PerformanceFact(consecutive_losses=P(lambda x: x >= 2)),
        salience=70,
    )
    def rule_medium_risk_rust_after_rest(self):
        """Medium risk: Long rest after struggles (rust factor)"""
        betting_rec = BettingRecommendation(
            risk_level="medium",
            reason="Long rest (4+ days) after recent struggles - potential rust",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "medium",
                "reason": "Long rest (4+ days) after recent struggles - potential rust",
            }
        )
        self.triggered_rules.append("Medium Risk: Rust factor")
        self.risk_factors.append("Extended rest following poor performance")

    @Rule(
        PerformanceFact(
            last_5_record=P(lambda x: BettingExpertEngine._parse_record(x)[1] >= 4)
        ),
        AvailabilityFact(key_players_unavailable=False),
        salience=65,
    )
    def rule_medium_risk_recent_collapse_healthy(self):
        """Medium risk: Recent collapse despite healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="medium",
            reason="Recent poor form (4+ losses in last 5) despite healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "medium",
                "reason": "Recent poor form (4+ losses in last 5) despite healthy roster",
            }
        )
        self.triggered_rules.append("Medium Risk: Healthy team underperforming")
        self.risk_factors.append("Poor recent form with full roster")

    @Rule(
        Fact(rest_days=P(lambda x: x == 0)),  # No rest
        VenueFact(venue="away"),
        salience=65,
    )
    def rule_medium_risk_no_rest_away(self):
        """Medium risk: No rest before away game"""
        betting_rec = BettingRecommendation(
            risk_level="medium", reason="No rest before away game (tired legs)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {"risk_level": "medium", "reason": "No rest before away game (tired legs)"}
        )
        self.triggered_rules.append("Medium Risk: No rest away")
        self.risk_factors.append("Playing away game without rest")

    # NEW SAFE BET RULES

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x > 0.75)),
        PerformanceFact(points_per_game=P(lambda x: x > 118)),
        PerformanceFact(opponent_points_per_game=P(lambda x: x < 108)),
        salience=90,
    )
    def rule_very_safe_super_elite_team(self):
        """Very safe: Championship-level team performance"""
        betting_rec = BettingRecommendation(
            risk_level="very_low",
            reason="Championship-level team (>75% wins, >118 PPG, <108 OPPG)",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "very_low",
                "reason": "Championship-level team (>75% wins, >118 PPG, <108 OPPG)",
            }
        )
        self.triggered_rules.append("Very Safe: Championship contender")
        self.safe_factors.append("Elite performance on both ends of court")

    @Rule(
        Fact(point_differential=P(lambda x: x > 8)),
        VenueFact(venue="home"),
        salience=75,
    )
    def rule_safe_dominant_point_differential_home(self):
        """Safe: Dominant team at home with great point differential"""
        betting_rec = BettingRecommendation(
            risk_level="low", reason="Dominant point differential (+8 per game) at home"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Dominant point differential (+8 per game) at home",
            }
        )
        self.triggered_rules.append("Safe Bet: Dominant team at home")
        self.safe_factors.append("Strong scoring margin in home environment")

    @Rule(
        PerformanceFact(
            last_5_record=P(lambda x: BettingExpertEngine._parse_record(x)[0] >= 4)
        ),
        VenueFact(venue="home"),
        salience=70,
    )
    def rule_safe_hot_recent_form_home(self):
        """Safe: Hot recent form at home"""
        betting_rec = BettingRecommendation(
            risk_level="low", reason="Hot recent form (4+ wins in last 5) at home"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Hot recent form (4+ wins in last 5) at home",
            }
        )
        self.triggered_rules.append("Safe Bet: Hot form at home")
        self.safe_factors.append("Excellent recent momentum in home environment")

    @Rule(
        PerformanceFact(consecutive_wins=P(lambda x: x >= 5)),
        VenueFact(venue="home"),
        AvailabilityFact(key_players_unavailable=False),
        salience=85,
    )
    def rule_very_safe_hot_home_team(self):
        """Very safe: Hot streak at home with full roster"""
        betting_rec = BettingRecommendation(
            risk_level="very_low",
            reason="Hot streak (5+ wins) at home with full roster - excellent momentum",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "very_low",
                "reason": "Hot streak (5+ wins) at home with full roster - excellent momentum",
            }
        )
        self.triggered_rules.append("Very Safe: Hot home team")
        self.safe_factors.append("Strong momentum at home with healthy roster")

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x > 0.7)),
        AvailabilityFact(key_players_unavailable=False),
        VenueFact(venue="home"),
        salience=80,
    )
    def rule_safe_dominant_team_home_healthy(self):
        """Safe: Dominant team at home with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Dominant team (>70% wins) at home with full roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Dominant team (>70% wins) at home with full roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Dominant team at home")
        self.safe_factors.append(
            "Strong team performance in home environment with full squad"
        )

    @Rule(
        PerformanceFact(consecutive_wins=P(lambda x: x >= 3)),
        PerformanceFact(points_per_game=P(lambda x: x > 115)),
        AvailabilityFact(key_players_unavailable=False),
        salience=75,
    )
    def rule_safe_hot_offensive_team_healthy(self):
        """Safe: Hot streak with strong offense and healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Hot streak (3+ wins) with strong offense (>115 PPG) and healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Hot streak (3+ wins) with strong offense (>115 PPG) and healthy roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Hot offensive team")
        self.safe_factors.append("Winning momentum with strong scoring and full roster")

    @Rule(
        PerformanceFact(
            home_record=P(lambda x: BettingExpertEngine._is_excellent_home_record(x))
        ),
        VenueFact(venue="home"),
        AvailabilityFact(key_players_unavailable=False),
        salience=70,
    )
    def rule_safe_fortress_home_team(self):
        """Safe: Excellent home record with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Excellent home record (>80% wins) with healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Excellent home record (>80% wins) with healthy roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Home fortress")
        self.safe_factors.append("Dominant home performance with full squad")

    @Rule(
        PerformanceFact(opponent_points_per_game=P(lambda x: x < 105)),
        VenueFact(venue="home"),
        PerformanceFact(win_percentage=P(lambda x: x > 0.6)),
        salience=65,
    )
    def rule_safe_elite_defense_home(self):
        """Safe: Elite defense at home"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Elite defense (<105 OPPG) at home with good record",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Elite defense (<105 OPPG) at home with good record",
            }
        )
        self.triggered_rules.append("Safe Bet: Elite defense at home")
        self.safe_factors.append("Strong defensive team in home environment")

    @Rule(
        Fact(rest_days=P(lambda x: 1 <= x <= 3)),
        PerformanceFact(consecutive_wins=P(lambda x: x >= 2)),
        VenueFact(venue="home"),
        salience=60,
    )
    def rule_safe_rested_winning_team_home(self):
        """Safe: Well-rested winning team at home"""
        betting_rec = BettingRecommendation(
            risk_level="low", reason="Well-rested (1-3 days) winning team at home"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Well-rested (1-3 days) winning team at home",
            }
        )
        self.triggered_rules.append("Safe Bet: Rested winners at home")
        self.safe_factors.append("Optimal rest with winning momentum at home")

    @Rule(
        PerformanceFact(
            last_10_record=P(lambda x: BettingExpertEngine._parse_record(x)[0] >= 8)
        ),
        AvailabilityFact(key_players_unavailable=False),
        salience=65,
    )
    def rule_safe_excellent_recent_form_healthy(self):
        """Safe: Excellent recent form with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Excellent recent form (8+ wins in last 10) with healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Excellent recent form (8+ wins in last 10) with healthy roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Excellent form")
        self.safe_factors.append("Sustained excellent performance with full squad")

    # ADDITIONAL SAFE BET RULES FOR BETTER BALANCE

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x > 0.65)),
        PerformanceFact(consecutive_wins=P(lambda x: x >= 4)),
        AvailabilityFact(key_players_unavailable=False),
        salience=80,
    )
    def rule_safe_elite_team_hot_streak_healthy(self):
        """Safe: Elite team on hot streak with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Elite team (>65% wins) on 4+ game winning streak with full roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Elite team (>65% wins) on 4+ game winning streak with full roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Elite team hot streak")
        self.safe_factors.append(
            "High-performing team with strong momentum and full roster"
        )

    @Rule(
        PerformanceFact(points_per_game=P(lambda x: x > 120)),
        PerformanceFact(win_percentage=P(lambda x: x > 0.6)),
        VenueFact(venue="home"),
        salience=75,
    )
    def rule_safe_explosive_offense_home(self):
        """Safe: Explosive offense at home with good record"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Explosive offense (>120 PPG) at home with good record",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Explosive offense (>120 PPG) at home with good record",
            }
        )
        self.triggered_rules.append("Safe Bet: Explosive offense at home")
        self.safe_factors.append("High-scoring team in favorable home environment")

    @Rule(
        Fact(point_differential=P(lambda x: x > 10)),
        AvailabilityFact(key_players_unavailable=False),
        salience=75,
    )
    def rule_safe_dominant_point_differential_healthy(self):
        """Safe: Dominant point differential with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Dominant point differential (+10 per game) with healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Dominant point differential (+10 per game) with healthy roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Dominant scoring margin")
        self.safe_factors.append(
            "Consistently outscoring opponents by large margin with full squad"
        )

    @Rule(
        PerformanceFact(consecutive_wins=P(lambda x: x >= 6)),
        AvailabilityFact(key_players_unavailable=False),
        salience=85,
    )
    def rule_very_safe_extended_hot_streak_healthy(self):
        """Very safe: Extended hot streak with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="very_low",
            reason="Extended hot streak (6+ wins) with full roster - peak momentum",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "very_low",
                "reason": "Extended hot streak (6+ wins) with full roster - peak momentum",
            }
        )
        self.triggered_rules.append("Very Safe: Extended hot streak")
        self.safe_factors.append("Exceptional momentum with healthy roster")

    @Rule(
        PerformanceFact(opponent_points_per_game=P(lambda x: x < 100)),
        PerformanceFact(win_percentage=P(lambda x: x > 0.65)),
        salience=80,
    )
    def rule_safe_lockdown_defense_elite(self):
        """Safe: Lockdown defense on elite team"""
        betting_rec = BettingRecommendation(
            risk_level="low", reason="Lockdown defense (<100 OPPG) on elite team"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Lockdown defense (<100 OPPG) on elite team",
            }
        )
        self.triggered_rules.append("Safe Bet: Lockdown defense")
        self.safe_factors.append("Elite defensive performance on strong team")

    @Rule(
        Fact(rest_days=P(lambda x: 2 <= x <= 3)),
        PerformanceFact(win_percentage=P(lambda x: x > 0.7)),
        VenueFact(venue="home"),
        salience=70,
    )
    def rule_safe_optimal_rest_elite_home(self):
        """Safe: Elite team with optimal rest at home"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Elite team (>70% wins) with optimal rest (2-3 days) at home",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Elite team (>70% wins) with optimal rest (2-3 days) at home",
            }
        )
        self.triggered_rules.append("Safe Bet: Elite team optimal rest")
        self.safe_factors.append("Strong team with perfect rest in home environment")

    @Rule(
        PerformanceFact(
            last_5_record=P(lambda x: BettingExpertEngine._parse_record(x)[0] == 5)
        ),
        VenueFact(venue="home"),
        AvailabilityFact(key_players_unavailable=False),
        salience=85,
    )
    def rule_very_safe_perfect_recent_form_home(self):
        """Very safe: Perfect recent form at home with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="very_low",
            reason="Perfect recent form (5-0 in last 5) at home with healthy roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "very_low",
                "reason": "Perfect recent form (5-0 in last 5) at home with healthy roster",
            }
        )
        self.triggered_rules.append("Very Safe: Perfect recent form")
        self.safe_factors.append("Flawless recent performance at home with full squad")

    @Rule(
        PerformanceFact(points_per_game=P(lambda x: x > 115)),
        PerformanceFact(opponent_points_per_game=P(lambda x: x < 110)),
        VenueFact(venue="home"),
        AvailabilityFact(key_players_unavailable=False),
        salience=75,
    )
    def rule_safe_balanced_excellence_home_healthy(self):
        """Safe: Balanced offensive/defensive excellence at home with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Strong offense (>115 PPG) and defense (<110 OPPG) at home with full roster",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "low",
                "reason": "Strong offense (>115 PPG) and defense (<110 OPPG) at home with full roster",
            }
        )
        self.triggered_rules.append("Safe Bet: Balanced excellence")
        self.safe_factors.append("Strong two-way play at home with healthy squad")

    # RIVALRY ANALYSIS RULES (MINIMAL IMPACT)

    @Rule(
        Fact(is_rivalry=True),
        Fact(rivalry_intensity="high"),
        salience=30,  # Low salience to minimize impact
    )
    def rule_rivalry_unpredictability_factor(self):
        """Minimal impact: High-intensity rivalry may add slight unpredictability"""
        betting_rec = BettingRecommendation(
            risk_level="medium",
            reason="Classic rivalry matchup - slight unpredictability factor",
        )
        self.declare(betting_rec)
        self.betting_recommendations.append(
            {
                "risk_level": "medium",
                "reason": "Classic rivalry matchup - slight unpredictability factor",
            }
        )
        self.triggered_rules.append("Info: Rivalry factor")
        # Note: Intentionally not adding to risk_factors to minimize impact

    # Neutral/Default Rules
    @Rule(
        PerformanceFact(win_percentage=P(lambda x: 0.45 <= x <= 0.6)),
        ~AvailabilityFact(key_players_unavailable=True),
        salience=50,
    )
    def rule_neutral_average_team(self):
        """Neutral: Average team without major concerns"""
        betting_rec = BettingRecommendation(
            risk_level="medium",
            reason="Average team performance with no major red flags",
        )

        self.declare(betting_rec)

        # Store in our own list for retrieval
        self.betting_recommendations.append(
            {
                "risk_level": "medium",
                "reason": "Average team performance with no major red flags",
            }
        )

        self.triggered_rules.append("Neutral: Average team")

    # NEW: COMPARATIVE MATCHUP RULES - Consider opponent statistics

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x > 0.7)),
        OpponentPerformanceFact(win_percentage=P(lambda x: x < 0.4)),
        salience=90,
    )
    def rule_safe_strong_vs_weak_team(self):
        """Safe: Strong team vs weak opponent"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Strong team (>70% wins) facing weak opponent (<40% wins)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Strong team (>70% wins) facing weak opponent (<40% wins)"
        })
        self.triggered_rules.append("Safe Bet: Strong vs weak matchup")
        self.safe_factors.append("Favorable matchup against struggling opponent")

    @Rule(
        PerformanceFact(win_percentage=P(lambda x: x < 0.4)),
        OpponentPerformanceFact(win_percentage=P(lambda x: x > 0.7)),
        salience=90,
    )
    def rule_high_risk_weak_vs_strong_team(self):
        """High risk: Weak team vs strong opponent"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Weak team (<40% wins) facing strong opponent (>70% wins)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "high",
            "reason": "Weak team (<40% wins) facing strong opponent (>70% wins)"
        })
        self.triggered_rules.append("High Risk: Weak vs strong matchup")
        self.risk_factors.append("Difficult matchup against superior opponent")

    @Rule(
        MatchupFact(offensive_advantage=P(lambda x: x > 10)),
        VenueFact(venue="home"),
        salience=75,
    )
    def rule_safe_major_offensive_advantage_home(self):
        """Safe: Major offensive advantage at home"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Major offensive advantage (>10 PPG) at home vs opponent"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Major offensive advantage (>10 PPG) at home vs opponent"
        })
        self.triggered_rules.append("Safe Bet: Major offensive advantage")
        self.safe_factors.append("Significant scoring advantage over opponent")

    @Rule(
        MatchupFact(defensive_advantage=P(lambda x: x > 8)),
        AvailabilityFact(key_players_unavailable=False),
        salience=75,
    )
    def rule_safe_major_defensive_advantage(self):
        """Safe: Major defensive advantage with healthy roster"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Major defensive advantage (opponent allows 8+ more PPG) with full roster"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Major defensive advantage (opponent allows 8+ more PPG) with full roster"
        })
        self.triggered_rules.append("Safe Bet: Defensive mismatch")
        self.safe_factors.append("Opponent's poor defense vs our healthy roster")

    @Rule(
        PerformanceFact(consecutive_wins=P(lambda x: x >= 3)),
        OpponentPerformanceFact(consecutive_losses=P(lambda x: x >= 3)),
        salience=80,
    )
    def rule_safe_hot_vs_cold_teams(self):
        """Safe: Hot team vs cold opponent"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Hot team (3+ wins) facing cold opponent (3+ losses)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Hot team (3+ wins) facing cold opponent (3+ losses)"
        })
        self.triggered_rules.append("Safe Bet: Hot vs cold momentum")
        self.safe_factors.append("Positive momentum against struggling opponent")

    @Rule(
        PerformanceFact(consecutive_losses=P(lambda x: x >= 2)),
        OpponentPerformanceFact(consecutive_wins=P(lambda x: x >= 3)),
        salience=80,
    )
    def rule_high_risk_cold_vs_hot_teams(self):
        """High risk: Cold team vs hot opponent"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Cold team (2+ losses) facing hot opponent (3+ wins)"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "high",
            "reason": "Cold team (2+ losses) facing hot opponent (3+ wins)"
        })
        self.triggered_rules.append("High Risk: Cold vs hot momentum")
        self.risk_factors.append("Poor momentum against surging opponent")

    @Rule(
        AvailabilityFact(key_players_unavailable=True),
        OpponentAvailabilityFact(key_players_unavailable=False),
        salience=85,
    )
    def rule_high_risk_injuries_vs_healthy_opponent(self):
        """High risk: Key players out vs healthy opponent"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Key players unavailable while opponent has full roster"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "high",
            "reason": "Key players unavailable while opponent has full roster"
        })
        self.triggered_rules.append("High Risk: Injuries vs healthy opponent")
        self.risk_factors.append("Roster disadvantage against healthy opponent")

    @Rule(
        AvailabilityFact(key_players_unavailable=False),
        OpponentAvailabilityFact(key_players_unavailable=True),
        salience=75,
    )
    def rule_safe_healthy_vs_injured_opponent(self):
        """Safe: Healthy roster vs injured opponent"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Full roster vs opponent with key players unavailable"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Full roster vs opponent with key players unavailable"
        })
        self.triggered_rules.append("Safe Bet: Health advantage")
        self.safe_factors.append("Roster advantage over injured opponent")

    @Rule(
        MatchupFact(win_percentage_diff=P(lambda x: x > 0.25)),
        VenueFact(venue="home"),
        salience=80,
    )
    def rule_safe_significant_quality_advantage_home(self):
        """Safe: Significant quality advantage at home"""
        betting_rec = BettingRecommendation(
            risk_level="low",
            reason="Significant quality advantage (25%+ win rate difference) at home"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "low",
            "reason": "Significant quality advantage (25%+ win rate difference) at home"
        })
        self.triggered_rules.append("Safe Bet: Quality mismatch at home")
        self.safe_factors.append("Superior team quality in home environment")

    @Rule(
        MatchupFact(win_percentage_diff=P(lambda x: x < -0.2)),
        VenueFact(venue="away"),
        salience=85,
    )
    def rule_high_risk_quality_disadvantage_away(self):
        """High risk: Quality disadvantage on the road"""
        betting_rec = BettingRecommendation(
            risk_level="high",
            reason="Quality disadvantage (20%+ win rate deficit) on the road"
        )
        self.declare(betting_rec)
        self.betting_recommendations.append({
            "risk_level": "high",
            "reason": "Quality disadvantage (20%+ win rate deficit) on the road"
        })
        self.triggered_rules.append("High Risk: Quality deficit away")
        self.risk_factors.append("Inferior team playing on opponent's court")

    @staticmethod
    def _parse_record(record_str: str) -> tuple:
        """Parse record string like '7-3' into (wins, losses)"""
        try:
            if "-" in record_str:
                wins, losses = record_str.split("-")
                return int(wins), int(losses)
        except:
            pass
        return 0, 0    @staticmethod
    def _is_terrible_road_record(record_str: str) -> bool:
        """Check if road record is terrible (<25% win rate)"""
        wins, losses = BettingExpertEngine._parse_record(record_str)
        total = wins + losses
        if total == 0:
            return False
        return (wins / total) < 0.25

    @staticmethod
    def _is_excellent_home_record(record_str: str) -> bool:
        """Check if home record is excellent (>80% win rate)"""
        wins, losses = BettingExpertEngine._parse_record(record_str)
        total = wins + losses
        if total == 0:
            return False
        return (wins / total) > 0.8

    def analyze_bet(
        self, team_stats: TeamStats, venue: str = "neutral", opponent_stats: TeamStats = None
    ) -> Dict[str, Any]:
        """
        Analyze betting recommendation for a team considering opponent
        """
        self.reset()
        self.reset_analysis()

        # Declare facts based on main team stats
        self.declare(TeamFact(name=team_stats.team_name))

        self.declare(
            PerformanceFact(
                win_percentage=team_stats.win_percentage,
                consecutive_wins=team_stats.consecutive_wins,
                consecutive_losses=team_stats.consecutive_losses,
                points_per_game=team_stats.points_per_game,
                opponent_points_per_game=team_stats.opponent_points_per_game,
                last_10_record=team_stats.last_10_games,
                home_record=team_stats.home_record,
                # Add new fields with fallback values
                last_5_record=getattr(team_stats, "last_5_games", "0-0"),
                away_record=getattr(team_stats, "away_record", "0-0"),
            )
        )

        self.declare(
            AvailabilityFact(
                key_players_unavailable=team_stats.key_players_unavailable,
                unavailable_count=len(team_stats.unavailable_players),
                key_players_count=team_stats.key_players_unavailable_count,
            )
        )

        self.declare(VenueFact(venue=venue))

        # Add new contextual facts
        point_diff = team_stats.points_per_game - team_stats.opponent_points_per_game
        self.declare(
            Fact(
                back_to_back=getattr(team_stats, "back_to_back", False),
                point_differential=point_diff,
                rest_days=getattr(team_stats, "rest_days", 1),
            )
        )

        # NEW: Declare opponent facts if available
        if opponent_stats:
            self.declare(OpponentFact(name=opponent_stats.team_name))
            
            self.declare(
                OpponentPerformanceFact(
                    win_percentage=opponent_stats.win_percentage,
                    consecutive_wins=opponent_stats.consecutive_wins,
                    consecutive_losses=opponent_stats.consecutive_losses,
                    points_per_game=opponent_stats.points_per_game,
                    opponent_points_per_game=opponent_stats.opponent_points_per_game,
                    last_10_record=opponent_stats.last_10_games,
                    home_record=opponent_stats.home_record,
                    last_5_record=getattr(opponent_stats, "last_5_games", "0-0"),
                    away_record=getattr(opponent_stats, "away_record", "0-0"),
                )
            )

            self.declare(
                OpponentAvailabilityFact(
                    key_players_unavailable=opponent_stats.key_players_unavailable,
                    unavailable_count=len(opponent_stats.unavailable_players),
                    key_players_count=opponent_stats.key_players_unavailable_count,
                )
            )

            # Calculate matchup differentials
            point_diff_matchup = team_stats.points_per_game - opponent_stats.points_per_game
            def_diff_matchup = opponent_stats.opponent_points_per_game - team_stats.opponent_points_per_game
            
            self.declare(
                MatchupFact(
                    offensive_advantage=point_diff_matchup,
                    defensive_advantage=def_diff_matchup,
                    win_percentage_diff=team_stats.win_percentage - opponent_stats.win_percentage,
                )
            )

            # Add rivalry analysis
            rivalry_data = getattr(team_stats, "rivalry_data", None)
            if rivalry_data:
                # Declare rivalry facts with minimal impact
                self.declare(
                    Fact(
                        is_rivalry=rivalry_data.get("is_rivalry", False),
                        rivalry_intensity=rivalry_data.get("intensity", "low"),
                        rivalry_impact_factor=rivalry_data.get("impact_factor", 1.0),
                    )
                )

        # Run the inference engine
        self.run()

        # Use our stored recommendations instead of searching through self.facts
        # Determine overall risk level with improved logic
        risk_levels = [rec["risk_level"] for rec in self.betting_recommendations]

        # Count different risk levels
        very_high_count = risk_levels.count("very_high")
        high_count = risk_levels.count("high")
        medium_count = risk_levels.count("medium")
        low_count = risk_levels.count("low")
        very_low_count = risk_levels.count("very_low")

        # Improved decision logic
        if very_high_count > 0 or high_count >= 2:
            overall_risk = "high"  # Map very_high to high for Bayesian compatibility
            recommendation = "avoid"
        elif high_count > 0:
            overall_risk = "high"
            recommendation = "risky"
        elif very_low_count >= 2 or (very_low_count >= 1 and low_count >= 1):
            overall_risk = "low"  # Map very_low to low for Bayesian compatibility
            recommendation = "highly_recommended"
        elif low_count >= 2 or (low_count >= 1 and medium_count == 0):
            overall_risk = "low"
            recommendation = "safe"
        elif low_count > high_count and medium_count <= 1:
            overall_risk = "low"
            recommendation = "safe"
        else:
            overall_risk = "medium"
            recommendation = "neutral"

        return {
            "recommendation": recommendation,
            "risk_level": overall_risk,
            "triggered_rules": self.triggered_rules,
            "risk_factors": self.risk_factors,
            "safe_factors": self.safe_factors,
            "reasoning": self.risk_factors + self.safe_factors,
        }
