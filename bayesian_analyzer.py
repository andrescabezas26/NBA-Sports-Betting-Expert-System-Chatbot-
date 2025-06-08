"""
Bayesian Network for NBA Betting Risk Assessment
Uses pgmpy to implement probabilistic reasoning
"""

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from models import TeamStats


class BayesianBettingAnalyzer:
    """Bayesian network for betting risk assessment"""

    def __init__(self):
        self.model = None
        self.inference = None
        self._build_network()

    def _build_network(self):
        """Build the Bayesian network structure"""
        # Define the network structure
        # Nodes: WinPercentage, AvailabilityStatus, RecentForm, Venue, BettingRisk
        self.model = BayesianNetwork(
            [
                ("WinPercentage", "BettingRisk"),
                ("AvailabilityStatus", "BettingRisk"),
                ("RecentForm", "BettingRisk"),
                ("Venue", "BettingRisk"),
                ("WinPercentage", "RecentForm"),
                ("AvailabilityStatus", "RecentForm"),
            ]
        )

        # Define CPDs (Conditional Probability Distributions)

        # Win Percentage CPD (marginal)
        cpd_win_pct = TabularCPD(
            variable="WinPercentage",
            variable_card=3,  # Poor, Average, Good
            values=[[0.25], [0.50], [0.25]],  # Prior probabilities
            state_names={"WinPercentage": ["Poor", "Average", "Good"]},
        )

        # Player Availability Status CPD (marginal)
        cpd_availability = TabularCPD(
            variable="AvailabilityStatus",
            variable_card=2,  # Available, Unavailable
            values=[[0.7], [0.3]],  # 70% available, 30% unavailable
            state_names={"AvailabilityStatus": ["Available", "Unavailable"]},
        )

        # Venue CPD (marginal)
        cpd_venue = TabularCPD(
            variable="Venue",
            variable_card=2,  # Home, Away
            values=[[0.5], [0.5]],  # Equal probability
            state_names={"Venue": ["Home", "Away"]},
        )

        # Recent Form CPD (depends on WinPercentage and AvailabilityStatus)
        cpd_recent_form = TabularCPD(
            variable="RecentForm",
            variable_card=3,  # Poor, Average, Good
            values=[
                # WinPct=Poor, Available | WinPct=Poor, Unavailable | WinPct=Avg, Available | WinPct=Avg, Unavailable | WinPct=Good, Available | WinPct=Good, Unavailable
                [0.7, 0.85, 0.4, 0.6, 0.2, 0.4],  # Poor form
                [0.25, 0.13, 0.45, 0.35, 0.3, 0.45],  # Average form
                [0.05, 0.02, 0.15, 0.05, 0.5, 0.15],  # Good form
            ],
            evidence=["WinPercentage", "AvailabilityStatus"],
            evidence_card=[3, 2],
            state_names={
                "RecentForm": ["Poor", "Average", "Good"],
                "WinPercentage": ["Poor", "Average", "Good"],
                "AvailabilityStatus": ["Available", "Unavailable"],
            },
        )

        # Betting Risk CPD (depends on all factors)
        # Order: WinPercentage x AvailabilityStatus x RecentForm x Venue
        # Total combinations: 3 x 2 x 3 x 2 = 36
        betting_risk_values = self._calculate_betting_risk_probabilities()

        cpd_betting_risk = TabularCPD(
            variable="BettingRisk",
            variable_card=3,  # Low, Medium, High
            values=betting_risk_values,
            evidence=["WinPercentage", "AvailabilityStatus", "RecentForm", "Venue"],
            evidence_card=[3, 2, 3, 2],
            state_names={
                "BettingRisk": ["Low", "Medium", "High"],
                "WinPercentage": ["Poor", "Average", "Good"],
                "AvailabilityStatus": ["Available", "Unavailable"],
                "RecentForm": ["Poor", "Average", "Good"],
                "Venue": ["Home", "Away"],
            },
        )

        # Add CPDs to the model
        self.model.add_cpds(
            cpd_win_pct, cpd_availability, cpd_venue, cpd_recent_form, cpd_betting_risk
        )

        # Validate the model
        assert self.model.check_model()

        # Initialize inference
        self.inference = VariableElimination(self.model)

    def _calculate_betting_risk_probabilities(self):
        """Calculate probabilities for betting risk based on evidence combinations"""
        # This creates a 3x36 matrix for Low, Medium, High risk
        # Based on expert knowledge and domain expertise

        risk_probs = []

        # Define base probabilities for different scenarios
        scenarios = [
            # (WinPct, Availability, RecentForm, Venue) -> (Low, Medium, High)
            ("Poor", "Available", "Poor", "Home"),  # 0.1, 0.3, 0.6
            ("Poor", "Available", "Poor", "Away"),  # 0.05, 0.25, 0.7
            ("Poor", "Available", "Average", "Home"),  # 0.15, 0.4, 0.45
            ("Poor", "Available", "Average", "Away"),  # 0.1, 0.35, 0.55
            ("Poor", "Available", "Good", "Home"),  # 0.25, 0.45, 0.3
            ("Poor", "Available", "Good", "Away"),  # 0.2, 0.4, 0.4
            ("Poor", "Unavailable", "Poor", "Home"),  # 0.05, 0.2, 0.75
            ("Poor", "Unavailable", "Poor", "Away"),  # 0.02, 0.15, 0.83
            ("Poor", "Unavailable", "Average", "Home"),  # 0.1, 0.3, 0.6
            ("Poor", "Unavailable", "Average", "Away"),  # 0.05, 0.25, 0.7
            ("Poor", "Unavailable", "Good", "Home"),  # 0.15, 0.35, 0.5
            ("Poor", "Unavailable", "Good", "Away"),  # 0.1, 0.3, 0.6
            ("Average", "Available", "Poor", "Home"),  # 0.2, 0.4, 0.4
            ("Average", "Available", "Poor", "Away"),  # 0.15, 0.35, 0.5
            ("Average", "Available", "Average", "Home"),  # 0.35, 0.45, 0.2
            ("Average", "Available", "Average", "Away"),  # 0.25, 0.45, 0.3
            ("Average", "Available", "Good", "Home"),  # 0.5, 0.35, 0.15
            ("Average", "Available", "Good", "Away"),  # 0.4, 0.4, 0.2
            ("Average", "Unavailable", "Poor", "Home"),  # 0.1, 0.3, 0.6
            ("Average", "Unavailable", "Poor", "Away"),  # 0.05, 0.25, 0.7
            ("Average", "Unavailable", "Average", "Home"),  # 0.2, 0.4, 0.4
            ("Average", "Unavailable", "Average", "Away"),  # 0.15, 0.35, 0.5
            ("Average", "Unavailable", "Good", "Home"),  # 0.3, 0.45, 0.25
            ("Average", "Unavailable", "Good", "Away"),  # 0.25, 0.4, 0.35
            ("Good", "Available", "Poor", "Home"),  # 0.3, 0.45, 0.25
            ("Good", "Available", "Poor", "Away"),  # 0.25, 0.4, 0.35
            ("Good", "Available", "Average", "Home"),  # 0.6, 0.3, 0.1
            ("Good", "Available", "Average", "Away"),  # 0.5, 0.35, 0.15
            ("Good", "Available", "Good", "Home"),  # 0.8, 0.15, 0.05
            ("Good", "Available", "Good", "Away"),  # 0.7, 0.25, 0.05
            ("Good", "Unavailable", "Poor", "Home"),  # 0.2, 0.4, 0.4
            ("Good", "Unavailable", "Poor", "Away"),  # 0.15, 0.35, 0.5
            ("Good", "Unavailable", "Average", "Home"),  # 0.4, 0.4, 0.2
            ("Good", "Unavailable", "Average", "Away"),  # 0.35, 0.4, 0.25
            ("Good", "Unavailable", "Good", "Home"),  # 0.6, 0.3, 0.1
            ("Good", "Unavailable", "Good", "Away"),  # 0.5, 0.35, 0.15
        ]

        # Probability values for each scenario [Low, Medium, High]
        prob_values = [
            [0.1, 0.3, 0.6],  # Poor/Available/Poor/Home
            [0.05, 0.25, 0.7],  # Poor/Available/Poor/Away
            [0.15, 0.4, 0.45],  # Poor/Available/Average/Home
            [0.1, 0.35, 0.55],  # Poor/Available/Average/Away
            [0.25, 0.45, 0.3],  # Poor/Available/Good/Home
            [0.2, 0.4, 0.4],  # Poor/Available/Good/Away
            [0.05, 0.2, 0.75],  # Poor/Unavailable/Poor/Home
            [0.02, 0.15, 0.83],  # Poor/Unavailable/Poor/Away
            [0.1, 0.3, 0.6],  # Poor/Unavailable/Average/Home
            [0.05, 0.25, 0.7],  # Poor/Unavailable/Average/Away
            [0.15, 0.35, 0.5],  # Poor/Unavailable/Good/Home
            [0.1, 0.3, 0.6],  # Poor/Unavailable/Good/Away
            [0.2, 0.4, 0.4],  # Average/Available/Poor/Home
            [0.15, 0.35, 0.5],  # Average/Available/Poor/Away
            [0.35, 0.45, 0.2],  # Average/Available/Average/Home
            [0.25, 0.45, 0.3],  # Average/Available/Average/Away
            [0.5, 0.35, 0.15],  # Average/Available/Good/Home
            [0.4, 0.4, 0.2],  # Average/Available/Good/Away
            [0.1, 0.3, 0.6],  # Average/Unavailable/Poor/Home
            [0.05, 0.25, 0.7],  # Average/Unavailable/Poor/Away
            [0.2, 0.4, 0.4],  # Average/Unavailable/Average/Home
            [0.15, 0.35, 0.5],  # Average/Unavailable/Average/Away
            [0.3, 0.45, 0.25],  # Average/Unavailable/Good/Home
            [0.25, 0.4, 0.35],  # Average/Unavailable/Good/Away
            [0.3, 0.45, 0.25],  # Good/Available/Poor/Home
            [0.25, 0.4, 0.35],  # Good/Available/Poor/Away
            [0.6, 0.3, 0.1],  # Good/Available/Average/Home
            [0.5, 0.35, 0.15],  # Good/Available/Average/Away
            [0.8, 0.15, 0.05],  # Good/Available/Good/Home
            [0.7, 0.25, 0.05],  # Good/Available/Good/Away
            [0.2, 0.4, 0.4],  # Good/Unavailable/Poor/Home
            [0.15, 0.35, 0.5],  # Good/Unavailable/Poor/Away
            [0.4, 0.4, 0.2],  # Good/Unavailable/Average/Home
            [0.35, 0.4, 0.25],  # Good/Unavailable/Average/Away
            [0.6, 0.3, 0.1],  # Good/Unavailable/Good/Home
            [0.5, 0.35, 0.15],  # Good/Unavailable/Good/Away
        ]

        # Transpose to get [Low_probs, Medium_probs, High_probs]
        return np.array(prob_values).T.tolist()

    def _categorize_win_percentage(self, win_pct: float) -> str:
        """Categorize win percentage"""
        if win_pct < 0.4:
            return "Poor"
        elif win_pct < 0.6:
            return "Average"
        else:
            return "Good"

    def _categorize_recent_form(self, last_10_record: str) -> str:
        """Categorize recent form based on last 10 games"""
        try:
            if "-" in last_10_record:
                wins, losses = map(int, last_10_record.split("-"))
                if wins >= 7:
                    return "Good"
                elif wins >= 4:
                    return "Average"
                else:
                    return "Poor"
        except:
            pass
        return "Average"

    def analyze_betting_risk(
        self, team_stats: TeamStats, venue: str = "Home"
    ) -> Dict[str, Any]:
        """
        Analyze betting risk using Bayesian inference
        """
        # Categorize inputs
        win_pct_category = self._categorize_win_percentage(team_stats.win_percentage)
        availability_status = (
            "Unavailable" if team_stats.key_players_unavailable else "Available"
        )
        recent_form = self._categorize_recent_form(team_stats.last_10_games)
        venue_category = venue.capitalize()

        # Perform inference
        evidence = {
            "WinPercentage": win_pct_category,
            "AvailabilityStatus": availability_status,
            "RecentForm": recent_form,
            "Venue": venue_category,
        }

        # Query for betting risk (suppress progress output)
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.inference.query(variables=["BettingRisk"], evidence=evidence)

        # Extract probabilities
        risk_probs = result.values
        risk_states = ["Low", "Medium", "High"]        # Find the most likely risk level - if there's a tie, choose the worst (highest) risk
        max_prob = np.max(risk_probs)
        # Find all indices with maximum probability
        max_indices = np.where(risk_probs == max_prob)[0]
        
        # If there's a tie, choose the highest risk (worst case scenario)
        if len(max_indices) > 1:
            max_prob_idx = max_indices[-1]  # Choose the last (highest risk) index
        else:
            max_prob_idx = max_indices[0]
            
        predicted_risk = risk_states[max_prob_idx]
        confidence = risk_probs[max_prob_idx]

        # Convert risk level to recommendation
        if predicted_risk == "Low":
            recommendation = "safe"
        else:
            recommendation = "risky"

        return {
            "risk_level": predicted_risk.lower(),
            "confidence": float(confidence),
            "recommendation": recommendation,
            "risk_probabilities": {
                "low": float(risk_probs[0]),
                "medium": float(risk_probs[1]),
                "high": float(risk_probs[2]),
            },
            "evidence": evidence,
            "bayesian_probability": float(confidence),
        }

    def explain_inference(self, team_stats: TeamStats, venue: str = "Home") -> str:
        """
        Provide explanation of the Bayesian inference
        """
        analysis = self.analyze_betting_risk(team_stats, venue)
        evidence = analysis["evidence"]

        explanation = f"""
Bayesian Network Analysis:
- Team Performance: {evidence['WinPercentage']} ({team_stats.win_percentage:.1%} win rate)
- Player Availability: {evidence['AvailabilityStatus']} ({len(team_stats.unavailable_players)} key players unavailable)
- Recent Form: {evidence['RecentForm']} ({team_stats.last_10_games} in last 10)
- Venue: {evidence['Venue']}

Risk Assessment:
- Low Risk: {analysis['risk_probabilities']['low']:.1%}
- Medium Risk: {analysis['risk_probabilities']['medium']:.1%}
- High Risk: {analysis['risk_probabilities']['high']:.1%}

Prediction: {analysis['risk_level'].upper()} risk ({analysis['confidence']:.1%} confidence)
Recommendation: {analysis['recommendation'].upper()} bet
        """

        return explanation.strip()
