"""
NBA Sports Betting Expert System
Data models and fact definitions for the expert system
"""

from experta import Fact
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class TeamStats:
    """Statistics for an NBA team"""

    team_name: str
    wins: int
    losses: int
    win_percentage: float
    points_per_game: float
    opponent_points_per_game: float
    home_record: str
    away_record: str
    last_10_games: str
    streak: str
    unavailable_players: List[str]  # All unavailable players with importance level
    key_players_unavailable: bool  # True if any key/star players are out
    consecutive_losses: int
    consecutive_wins: int
    key_players_unavailable_count: int = 0  # Number of key players unavailable
    
    # New fields for enhanced analysis - factible with NBA API
    last_5_games: str = "0-0"  # Last 5 games record
    back_to_back: bool = False  # Is team playing back-to-back games
    rest_days: int = 1  # Days of rest before game
    point_differential: float = 0.0  # Average point differential per game
    
    def __post_init__(self):
        """Calculate point differential after initialization"""
        if self.point_differential == 0.0:
            self.point_differential = self.points_per_game - self.opponent_points_per_game


@dataclass
class GameInfo:
    """Information about an NBA game"""

    home_team: str
    away_team: str
    date: str
    time: str
    venue: Optional[str] = None
    event_id: Optional[str] = None


@dataclass
class BettingAnalysis:
    """Result of betting analysis"""

    recommendation: str  # "safe" or "risky"
    confidence: float
    risk_level: str  # "low", "medium", "high"
    reasoning: List[str]
    triggered_rules: List[str]
    bayesian_probability: float


# Experta Facts
class TeamFact(Fact):
    """Fact representing team information"""

    pass


class GameFact(Fact):
    """Fact representing game information"""

    pass


class AvailabilityFact(Fact):
    """Fact representing player availability information"""

    pass


class PerformanceFact(Fact):
    """Fact representing team performance"""
    # Fields: win_percentage, consecutive_wins, consecutive_losses, 
    # points_per_game, opponent_points_per_game, last_10_record, 
    # home_record, away_record, last_5_record
    pass


class VenueFact(Fact):
    """Fact representing venue/location information"""

    pass


class BettingRecommendation(Fact):
    """Fact representing betting recommendation"""

    pass


# NEW: Additional fact classes for opponent analysis
class OpponentFact(Fact):
    """Fact representing opponent team information"""

    pass


class OpponentPerformanceFact(Fact):
    """Fact representing opponent team performance"""

    pass


class OpponentAvailabilityFact(Fact):
    """Fact representing opponent player availability"""

    pass


class MatchupFact(Fact):
    """Fact representing head-to-head matchup information"""

    pass
