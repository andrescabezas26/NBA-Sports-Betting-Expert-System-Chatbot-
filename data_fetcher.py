"""
NBA Data Fetcher
Handles data retrieval from TheSportsDB and nba_api with caching
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from nba_api.stats.endpoints import teamgamelog, leaguegamefinder, playercareerstats
from nba_api.stats.static import teams, players
from models import GameInfo, TeamStats
import time


class NBADataFetcher:
    """Fetches NBA data from various sources with caching"""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.create_cache_dir()
        self.thesportsdb_url = (
            "https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id=4387"
        )
        # Load JSON data files
        self.star_players_data = self._load_star_players()
        self.rivalries_data = self._load_rivalries()

    def _load_star_players(self) -> Dict:
        """Load star players data from JSON file"""
        try:
            with open("star_players.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load star_players.json: {e}")
            return {}

    def _load_rivalries(self) -> List[Dict]:
        """Load rivalries data from JSON file"""
        try:
            with open("rivalries_derbies.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load rivalries_derbies.json: {e}")
            return []

    def check_rivalry_factor(self, home_team: str, away_team: str) -> Dict[str, any]:
        """
        Check if the matchup is a rivalry/derby and return intensity info
        Returns low-impact factor to not heavily influence betting decisions
        """
        rivalry_info = {
            "is_rivalry": False,
            "rivalry_name": "",
            "intensity": "normal",
            "description": "",
            "impact_factor": 1.0,  # Neutral impact by default
        }

        # Normalize team names for comparison
        home_normalized = self._normalize_team_name(home_team)
        away_normalized = self._normalize_team_name(away_team)

        for rivalry in self.rivalries_data:
            if rivalry.get("type") == "rivalry":
                teams_in_rivalry = [
                    self._normalize_team_name(team) for team in rivalry.get("teams", [])
                ]

                if (
                    home_normalized in teams_in_rivalry
                    and away_normalized in teams_in_rivalry
                ):
                    rivalry_info.update(
                        {
                            "is_rivalry": True,
                            "rivalry_name": rivalry.get("rivalry", ""),
                            "intensity": self._determine_rivalry_intensity(rivalry),
                            "description": rivalry.get("description", ""),
                            "impact_factor": self._calculate_rivalry_impact(rivalry),
                        }
                    )
                    break

        return rivalry_info

    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team name for comparison"""
        # Remove common prefixes and normalize
        normalized = team_name.lower().strip()

        # Handle common variations
        team_mappings = {
            "lakers": "Los Angeles Lakers",
            "warriors": "Golden State Warriors",
            "celtics": "Boston Celtics",
            "bulls": "Chicago Bulls",
            "heat": "Miami Heat",
            "knicks": "New York Knicks",
            "nets": "Brooklyn Nets",
            "sixers": "Philadelphia 76ers",
            "76ers": "Philadelphia 76ers",
            "raptors": "Toronto Raptors",
            "bucks": "Milwaukee Bucks",
            "cavaliers": "Cleveland Cavaliers",
            "cavs": "Cleveland Cavaliers",
            "pistons": "Detroit Pistons",
            "pacers": "Indiana Pacers",
            "hawks": "Atlanta Hawks",
            "hornets": "Charlotte Hornets",
            "magic": "Orlando Magic",
            "wizards": "Washington Wizards",
            "mavs": "Dallas Mavericks",
            "mavericks": "Dallas Mavericks",
            "rockets": "Houston Rockets",
            "grizzlies": "Memphis Grizzlies",
            "pelicans": "New Orleans Pelicans",
            "spurs": "San Antonio Spurs",
            "nuggets": "Denver Nuggets",
            "timberwolves": "Minnesota Timberwolves",
            "thunder": "Oklahoma City Thunder",
            "blazers": "Portland Trail Blazers",
            "jazz": "Utah Jazz",
            "suns": "Phoenix Suns",
            "kings": "Sacramento Kings",
            "clippers": "LA Clippers",
        } 
        return team_mappings.get(normalized, normalized)

    def _determine_rivalry_intensity(self, rivalry: Dict) -> str:
        """Determine rivalry intensity based on era and description"""
        era = rivalry.get("era", "").lower()
        description = rivalry.get("description", "").lower()

        # Modern rivalries are more intense
        if "present" in era or "2020s" in era or "2010s" in era:
            return "high"
        elif "2000s" in era or "1990s" in era:
            return "medium"
        else:
            return "low"

    def _calculate_rivalry_impact(self, rivalry: Dict) -> float:
        """
        Calculate minimal impact factor for rivalries
        Keep impact low to not heavily influence betting decisions
        """
        intensity = self._determine_rivalry_intensity(rivalry)

        # Very small impact factors to avoid major influence
        impact_factors = {
            "high": 1.05,  # 5% increase in unpredictability
            "medium": 1.03,  # 3% increase
            "low": 1.01,  # 1% increase
        }

        return impact_factors.get(intensity, 1.0)

    def create_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _is_cache_valid(self, cache_file: str, hours: int = 24) -> bool:
        """Check if cache file is still valid based on time"""
        if not os.path.exists(cache_file):
            return False

        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - file_time < timedelta(hours=hours)

    def get_upcoming_games(self, force_refresh: bool = False) -> List[GameInfo]:
        """
        Get upcoming NBA games from TheSportsDB with caching
        Cache is valid for 24 hours
        """
        cache_file = os.path.join(self.cache_dir, "upcoming_games.json")

        if not force_refresh and self._is_cache_valid(cache_file, 24):
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                return [GameInfo(**game) for game in cached_data]
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        try:
            print("Fetching upcoming games from TheSportsDB...")
            response = requests.get(self.thesportsdb_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            games = []

            if data and "events" in data and data["events"]:
                for event in data["events"]:
                    if event and "strHomeTeam" in event and "strAwayTeam" in event:
                        game = GameInfo(
                            home_team=event["strHomeTeam"],
                            away_team=event["strAwayTeam"],
                            date=event.get("dateEvent", ""),
                            time=event.get("strTime", ""),
                            venue=event.get("strVenue", ""),
                            event_id=event.get("idEvent", ""),
                        )
                        games.append(game)

            # Cache the results
            games_data = [game.__dict__ for game in games]
            with open(cache_file, "w") as f:
                json.dump(games_data, f, indent=2)

            print(f"Fetched {len(games)} upcoming games")
            return games

        except Exception as e:
            print(f"Error fetching upcoming games: {e}")
            # Try to return cached data even if expired
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                print("Using cached data due to API error")
                return [GameInfo(**game) for game in cached_data]
            except:
                print("No cached data available")
                return []

    def get_team_id(self, team_name: str) -> Optional[int]:
        """Get NBA team ID from team name"""
        nba_teams = teams.get_teams()

        # Direct match
        for team in nba_teams:
            if team_name.lower() in [
                team["full_name"].lower(),
                team["nickname"].lower(),
                team["city"].lower(),
            ]:
                return team["id"]

        # Fuzzy matching for common abbreviations and alternate names
        team_mappings = {
            "lakers": "Los Angeles Lakers",
            "warriors": "Golden State Warriors",
            "celtics": "Boston Celtics",
            "bulls": "Chicago Bulls",
            "heat": "Miami Heat",
            "knicks": "New York Knicks",
            "nets": "Brooklyn Nets",
            "sixers": "Philadelphia 76ers",
            "76ers": "Philadelphia 76ers",
            "raptors": "Toronto Raptors",
            "bucks": "Milwaukee Bucks",
            "cavaliers": "Cleveland Cavaliers",
            "cavs": "Cleveland Cavaliers",
            "pistons": "Detroit Pistons",
            "pacers": "Indiana Pacers",
            "hawks": "Atlanta Hawks",
            "hornets": "Charlotte Hornets",
            "magic": "Orlando Magic",
            "wizards": "Washington Wizards",
            "mavs": "Dallas Mavericks",
            "mavericks": "Dallas Mavericks",
            "rockets": "Houston Rockets",
            "grizzlies": "Memphis Grizzlies",
            "pelicans": "New Orleans Pelicans",
            "spurs": "San Antonio Spurs",
            "nuggets": "Denver Nuggets",
            "timberwolves": "Minnesota Timberwolves",
            "thunder": "Oklahoma City Thunder",
            "blazers": "Portland Trail Blazers",
            "jazz": "Utah Jazz",
            "suns": "Phoenix Suns",
            "kings": "Sacramento Kings",
            "clippers": "LA Clippers",
        }

        normalized_name = team_name.lower().strip()
        if normalized_name in team_mappings:
            full_name = team_mappings[normalized_name]
            for team in nba_teams:
                if team["full_name"].lower() == full_name.lower():
                    return team["id"]

        return None

    def get_team_stats(self, team_name: str) -> Optional[TeamStats]:
        """Get comprehensive team statistics"""
        team_id = self.get_team_id(team_name)
        if not team_id:
            print(f"Team '{team_name}' not found")
            return None

        try:
            print(f"Fetching stats for {team_name}...")

            # Get recent game log (last 10 games)
            game_log = teamgamelog.TeamGameLog(
                team_id=team_id, season="2024-25", season_type_all_star="Regular Season"
            )

            # Add delay to respect API limits
            time.sleep(0.6)

            games_df = game_log.get_data_frames()[0]

            if games_df.empty:
                print(f"No game data found for {team_name}")
                return None

            # Debug: Print available columns
            print(f"Available columns: {list(games_df.columns)}")

            # Calculate statistics
            total_games = len(games_df)
            wins = len(games_df[games_df["WL"] == "W"])
            losses = total_games - wins
            win_pct = wins / total_games if total_games > 0 else 0

            avg_points = games_df["PTS"].mean()

            # NBA API doesn't provide opponent points directly in team game log
            # We need to calculate it differently or use league averages
            # For now, let's use a reasonable NBA average
            avg_opp_points = 115.0  # Current NBA average points per game

            print(f"Team averages {avg_points:.1f} points per game")

            # Get last 10 games record
            last_10 = games_df.head(10)
            last_10_wins = len(last_10[last_10["WL"] == "W"])
            last_10_record = f"{last_10_wins}-{10 - last_10_wins}"

            # Calculate consecutive wins/losses
            consecutive_wins = 0
            consecutive_losses = 0
            current_streak = ""

            if not games_df.empty:
                # Get the most recent result
                recent_result = games_df.iloc[0]["WL"]
                streak_count = 1

                # Count consecutive results
                for i in range(1, min(len(games_df), 10)):
                    if games_df.iloc[i]["WL"] == recent_result:
                        streak_count += 1
                    else:
                        break

                if recent_result == "W":
                    consecutive_wins = streak_count
                    current_streak = f"W{streak_count}"
                else:
                    consecutive_losses = streak_count
                    current_streak = f"L{streak_count}"

            # Get unavailable players using NBA API
            try:
                unavailable_players = self.get_unavailable_players(team_id)
                print(
                    f"Found {len(unavailable_players)} unavailable players via NBA API"
                )

                # Count key players that are unavailable (marked with ⭐)
                key_players_out = [
                    p for p in unavailable_players if "⭐ Key Player" in p
                ]
                key_players_unavailable = len(key_players_out) > 0
                key_players_unavailable_count = len(key_players_out)

                if key_players_out:
                    print(f"⚠️  {len(key_players_out)} KEY PLAYERS unavailable:")
                    for player in key_players_out:
                        print(f"   - {player}")

            except Exception as e:
                print(f"Failed to get unavailable players from NBA API: {e}")
                # Fallback to mock data
                unavailable_players = self._get_mock_unavailable_players(team_name)
                key_players_out = [
                    p for p in unavailable_players if "⭐ Key Player" in p
                ]
                key_players_unavailable = len(key_players_out) > 0
                key_players_unavailable_count = len(key_players_out)
                print(
                    f"Using mock data: {len(unavailable_players)} unavailable players"
                )

            # Calculate home/away records (simplified)
            home_games = games_df[games_df["MATCHUP"].str.contains("vs.")]
            away_games = games_df[games_df["MATCHUP"].str.contains("@")]

            home_wins = len(home_games[home_games["WL"] == "W"])
            home_losses = len(home_games) - home_wins
            away_wins = len(away_games[away_games["WL"] == "W"])
            away_losses = len(away_games) - away_wins

            team_stats = TeamStats(
                team_name=team_name,
                wins=wins,
                losses=losses,
                win_percentage=win_pct,
                points_per_game=avg_points,
                opponent_points_per_game=avg_opp_points,
                home_record=f"{home_wins}-{home_losses}",
                away_record=f"{away_wins}-{away_losses}",
                last_10_games=last_10_record,
                streak=current_streak,
                unavailable_players=unavailable_players,
                key_players_unavailable=key_players_unavailable,
                key_players_unavailable_count=key_players_unavailable_count,
                consecutive_losses=consecutive_losses,
                consecutive_wins=consecutive_wins,
            )

            return team_stats

        except Exception as e:
            print(f"Error fetching team stats for {team_name}: {e}")
            return None

    def get_unavailable_players(self, team_id: int) -> List[str]:
        """
        Get players who are unavailable to play using NBA API
        Also analyzes their statistics to determine if they are key players
        """
        from nba_api.stats.endpoints import commonteamroster, playergamelog
        import time

        try:
            # Get team roster
            roster = commonteamroster.CommonTeamRoster(team_id=team_id)
            time.sleep(0.6)  # Respect API rate limits

            roster_df = roster.get_data_frames()[0]

            # Get player IDs
            player_ids = roster_df["PLAYER_ID"].tolist()

            unavailable = []
            key_players_out = []

            # Check each player's availability and importance
            for player_id in player_ids:
                try:
                    # Get recent game logs to check availability
                    games = playergamelog.PlayerGameLog(
                        player_id=player_id, season="2024-25"
                    )
                    time.sleep(0.6)
                    games_df = games.get_data_frames()[0]

                    # Get player name
                    player_name = roster_df[roster_df["PLAYER_ID"] == player_id][
                        "PLAYER"
                    ].values[0]

                    if games_df.empty or len(games_df) < 3:
                        # Player hasn't played recently - analyze their importance
                        player_stats = self._analyze_player_importance(
                            games_df, player_name
                        )

                        if player_stats["is_key_player"]:
                            unavailable.append(
                                f"{player_name} (⭐ Key Player - {player_stats['reason']})"
                            )
                            key_players_out.append(player_name)
                        else:
                            unavailable.append(
                                f"{player_name} (Role Player - {player_stats['reason']})"
                            )

                except Exception as e:
                    # If we can't get data, assume they might be unavailable
                    player_name = roster_df[roster_df["PLAYER_ID"] == player_id][
                        "PLAYER"
                    ].values[0]
                    unavailable.append(f"{player_name} (Status unknown)")

            # Store key players info for later use
            self._key_players_unavailable = key_players_out

            return unavailable

        except Exception as e:
            print(f"Error getting unavailable players: {e}")
            return []

    def _analyze_player_importance(self, games_df, player_name: str) -> dict:
        """
        Analyze if a player is a key player based on their statistics
        """
        if games_df.empty:
            # No recent games - check if they're a known star
            return self._classify_player_by_name(player_name)

        # Analyze stats from available games
        avg_points = games_df["PTS"].mean() if not games_df.empty else 0
        avg_rebounds = games_df["REB"].mean() if not games_df.empty else 0
        avg_assists = games_df["AST"].mean() if not games_df.empty else 0
        avg_minutes = games_df["MIN"].mean() if not games_df.empty else 0

        # Convert minutes from string format (MM:SS) to float
        if isinstance(avg_minutes, str):
            try:
                minutes_parts = avg_minutes.split(":")
                avg_minutes = float(minutes_parts[0]) + float(minutes_parts[1]) / 60
            except:
                avg_minutes = 0

        # Criteria for key player
        is_key_player = False
        reason = "Not in recent games"

        if avg_points >= 15 or avg_rebounds >= 8 or avg_assists >= 6:
            is_key_player = True
            reason = (
                f"Avg: {avg_points:.1f}pts, {avg_rebounds:.1f}reb, {avg_assists:.1f}ast"
            )
        elif avg_minutes >= 25:
            is_key_player = True
            reason = f"Starter - {avg_minutes:.1f} min/game"
        elif avg_points >= 10 and avg_minutes >= 20:
            is_key_player = True
            reason = f"Impact player - {avg_points:.1f}pts, {avg_minutes:.1f}min"

        return {
            "is_key_player": is_key_player,
            "reason": reason,
            "stats": {
                "points": avg_points,
                "rebounds": avg_rebounds,
                "assists": avg_assists,
                "minutes": avg_minutes,
            },
        }

    def _classify_player_by_name(self, player_name: str) -> dict:
        """
        Classify player importance based on star players loaded from JSON
        This is a fallback when we don't have statistical data
        """
        # Search through the star players data loaded from JSON
        for team_name, players in self.star_players_data.items():
            for star_name, description in players.items():
                if (
                    star_name.lower() in player_name.lower()
                    or player_name.lower() in star_name.lower()
                ):
                    return {"is_key_player": True, "reason": description, "stats": {}}

        return {
            "is_key_player": False,
            "reason": "Role player - not in recent games",
            "stats": {},
        }

    def _get_mock_unavailable_players(self, team_name: str) -> List[str]:
        """
        Mock unavailable players data - fallback when API fails
        Now includes analysis of player importance
        """
        # Simulate some unavailable players with their importance level
        mock_unavailable = {
            "Los Angeles Lakers": [
                "Anthony Davis (⭐ Key Player - Star - 24+ pts, 10+ reb, dominant defender)",
                "Rui Hachimura (Role Player - 10+ pts, solid contributor)",
            ],
            "Golden State Warriors": [
                "Andrew Wiggins (Role Player - 15+ pts, good defender)"
            ],
            "Boston Celtics": [],
            "Miami Heat": ["Tyler Herro (⭐ Key Player - 20+ pts, important scorer)"],
            "Chicago Bulls": ["Lonzo Ball (⭐ Key Player - Elite defender, playmaker)"],
            "Phoenix Suns": [],
            "Milwaukee Bucks": [],
            "Denver Nuggets": [],
            "Memphis Grizzlies": [
                "Ja Morant (⭐ Key Player - Dynamic playmaker, 25+ pts)"
            ],
            "Dallas Mavericks": [],
            "Oklahoma City Thunder": [],
            "Indiana Pacers": [],
        }

        # Find the team name that matches
        for team, unavailable in mock_unavailable.items():
            if team_name.lower() in team.lower() or team.lower() in team_name.lower():
                return unavailable

        return []

    def get_available_teams(self) -> List[str]:
        """Get list of all NBA teams"""
        nba_teams = teams.get_teams()
        return [team["full_name"] for team in nba_teams]
