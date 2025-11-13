"""
CFBD API Client for College Football Data

This module provides a client for fetching data from CollegeFootballData.com API.
Requires API key from https://collegefootballdata.com

Usage:
    from src.scrapers import CFBDClient

    client = CFBDClient()
    teams = client.get_teams(2025)
    schedule = client.get_schedule(2025, week=1)
    lines = client.get_betting_lines(2025, week=1)
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

import pandas as pd

# Try to import cfbd, but gracefully handle if not installed
try:
    import cfbd
    CFBD_AVAILABLE = True
except ImportError:
    CFBD_AVAILABLE = False
    logging.warning(
        "cfbd package not installed. "
        "Install with: pip install cfbd"
    )

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning(
        "python-dotenv package not installed. "
        "Install with: pip install python-dotenv"
    )


class CFBDClient:
    """
    Client for fetching data from CollegeFootballData.com API

    Attributes:
        configuration: CFBD API configuration object
        cache_dir: Directory for caching API responses

    Example:
        >>> client = CFBDClient()
        >>> teams = client.get_teams(2025)
        >>> print(f"Fetched {len(teams)} teams")
    """

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize CFBD API client

        Args:
            api_key: CFBD API key. If None, reads from CFBD_API_KEY env var
            cache_dir: Directory for caching responses. Defaults to project root/data/cache

        Raises:
            ImportError: If cfbd package not installed
            ValueError: If API key not provided and not in environment
        """
        if not CFBD_AVAILABLE:
            raise ImportError(
                "cfbd package is required. Install with: pip install cfbd"
            )

        # Load environment variables
        if DOTENV_AVAILABLE:
            load_dotenv()

        # Get API key
        self.api_key = api_key or os.getenv('CFBD_API_KEY')
        if not self.api_key:
            raise ValueError(
                "CFBD API key not found. Either:\n"
                "1. Pass api_key parameter to CFBDClient()\n"
                "2. Set CFBD_API_KEY environment variable\n"
                "3. Add CFBD_API_KEY to .env file\n"
                "Get an API key at: https://collegefootballdata.com"
            )

        # Configure CFBD client
        self.configuration = cfbd.Configuration()
        self.configuration.access_token = self.api_key

        # Set up caching
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            project_root = Path(__file__).parent.parent.parent
            self.cache_dir = project_root / "data" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def get_teams(self, year: int = 2025, conference: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch all FBS teams for a given year

        Args:
            year: Season year (e.g., 2025)
            conference: Optional conference filter

        Returns:
            DataFrame with columns:
                - team_id: Unique team identifier
                - name: Team name
                - mascot: Team mascot
                - abbreviation: Team abbreviation
                - conference: Conference name
                - division: FBS, FCS, etc.
                - latitude: Geographic latitude
                - longitude: Geographic longitude
                - location: City, State
                - color: Primary color hex
                - alt_color: Secondary color hex
                - logos: List of logo URLs

        Example:
            >>> teams = client.get_teams(2025)
            >>> fbs_teams = teams[teams['division'] == 'fbs']
            >>> print(f"{len(fbs_teams)} FBS teams")
        """
        cache_file = self.cache_dir / f"teams_{year}.csv"

        # Check cache first
        if cache_file.exists():
            self.logger.info(f"Loading teams from cache: {cache_file}")
            return pd.read_csv(cache_file)

        self.logger.info(f"Fetching teams for {year} from CFBD API")

        with cfbd.ApiClient(self.configuration) as api_client:
            teams_api = cfbd.TeamsApi(api_client)

            try:
                teams = teams_api.get_teams(year=year, conference=conference)
            except Exception as e:
                self.logger.error(f"Error fetching teams: {e}")
                raise

            # Convert to DataFrame
            teams_data = []
            for t in teams:
                if t.division == 'fbs':  # Only FBS teams
                    teams_data.append({
                        'team_id': t.id,
                        'name': t.school,
                        'mascot': t.mascot,
                        'abbreviation': t.abbreviation,
                        'conference': t.conference,
                        'division': t.division,
                        'latitude': t.latitude,
                        'longitude': t.longitude,
                        'location': t.location if hasattr(t, 'location') else None,
                        'color': t.color,
                        'alt_color': t.alt_color,
                        'logos': str(t.logos) if hasattr(t, 'logos') else None
                    })

            df = pd.DataFrame(teams_data)

            # Cache the results
            df.to_csv(cache_file, index=False)
            self.logger.info(f"Cached {len(df)} teams to {cache_file}")

            return df

    def get_schedule(
        self,
        year: int = 2025,
        week: Optional[int] = None,
        season_type: str = 'regular',
        team: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch schedule for a given year and optional week

        Args:
            year: Season year (e.g., 2025)
            week: Week number (1-15). If None, fetches all weeks
            season_type: 'regular' or 'postseason'
            team: Optional team name filter

        Returns:
            DataFrame with columns:
                - game_id: Unique game identifier
                - season: Season year
                - week: Week number
                - season_type: 'regular' or 'postseason'
                - date: Game date/time
                - home_team: Home team name
                - away_team: Away team name
                - home_conference: Home team conference
                - away_conference: Away team conference
                - venue: Stadium name
                - neutral_site: Boolean
                - conference_game: Boolean
                - home_score: Home team score (if completed)
                - away_score: Away team score (if completed)

        Example:
            >>> schedule = client.get_schedule(2025, week=1)
            >>> print(f"{len(schedule)} games in Week 1")
        """
        # Build cache filename
        if week:
            cache_file = self.cache_dir / f"schedule_{year}_week{week}.csv"
        else:
            cache_file = self.cache_dir / f"schedule_{year}_all.csv"

        # Check cache (only for completed weeks or full season)
        if cache_file.exists() and not team:
            self.logger.info(f"Loading schedule from cache: {cache_file}")
            return pd.read_csv(cache_file)

        self.logger.info(
            f"Fetching schedule for {year} "
            f"{'week ' + str(week) if week else 'all weeks'} from CFBD API"
        )

        with cfbd.ApiClient(self.configuration) as api_client:
            games_api = cfbd.GamesApi(api_client)

            try:
                if week:
                    games = games_api.get_games(
                        year=year,
                        week=week,
                        season_type=season_type,
                        division='fbs',
                        team=team
                    )
                else:
                    # Fetch all weeks (1-15 for regular season)
                    games = []
                    for w in range(1, 16):
                        self.logger.info(f"Fetching week {w}...")
                        week_games = games_api.get_games(
                            year=year,
                            week=w,
                            season_type=season_type,
                            division='fbs'
                        )
                        games.extend(week_games)

            except Exception as e:
                self.logger.error(f"Error fetching schedule: {e}")
                raise

            # Convert to DataFrame
            schedule_data = []
            for g in games:
                schedule_data.append({
                    'game_id': g.id,
                    'season': g.season,
                    'week': g.week,
                    'season_type': g.season_type,
                    'date': g.start_date,
                    'home_team': g.home_team,
                    'away_team': g.away_team,
                    'home_conference': g.home_conference,
                    'away_conference': g.away_conference,
                    'venue': g.venue,
                    'neutral_site': g.neutral_site,
                    'conference_game': g.conference_game,
                    'home_score': g.home_points,
                    'away_score': g.away_points
                })

            df = pd.DataFrame(schedule_data)

            # Cache the results (only if not filtered by team)
            if not team:
                df.to_csv(cache_file, index=False)
                self.logger.info(f"Cached {len(df)} games to {cache_file}")

            return df

    def get_betting_lines(
        self,
        year: int = 2025,
        week: Optional[int] = None,
        season_type: str = 'regular',
        team: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch betting lines for a given year and optional week

        Args:
            year: Season year (e.g., 2025)
            week: Week number (1-15). If None, fetches all weeks
            season_type: 'regular' or 'postseason'
            team: Optional team name filter

        Returns:
            DataFrame with columns:
                - game_id: Unique game identifier
                - season: Season year
                - week: Week number
                - home_team: Home team name
                - away_team: Away team name
                - spread: Point spread (negative for favorite)
                - formatted_spread: Human-readable spread
                - total: Over/Under total points
                - provider: Sportsbook name

        Example:
            >>> lines = client.get_betting_lines(2025, week=1)
            >>> print(f"{len(lines)} games with betting lines")
        """
        # Build cache filename
        if week:
            cache_file = self.cache_dir / f"betting_lines_{year}_week{week}.csv"
        else:
            cache_file = self.cache_dir / f"betting_lines_{year}_all.csv"

        # Check cache (only for completed weeks or full season)
        if cache_file.exists() and not team:
            self.logger.info(f"Loading betting lines from cache: {cache_file}")
            return pd.read_csv(cache_file)

        self.logger.info(
            f"Fetching betting lines for {year} "
            f"{'week ' + str(week) if week else 'all weeks'} from CFBD API"
        )

        with cfbd.ApiClient(self.configuration) as api_client:
            betting_api = cfbd.BettingApi(api_client)

            try:
                if week:
                    lines = betting_api.get_lines(
                        year=year,
                        week=week,
                        season_type=season_type,
                        team=team
                    )
                else:
                    # Fetch all weeks
                    lines = []
                    for w in range(1, 16):
                        self.logger.info(f"Fetching betting lines for week {w}...")
                        week_lines = betting_api.get_lines(
                            year=year,
                            week=w,
                            season_type=season_type
                        )
                        lines.extend(week_lines)

            except Exception as e:
                self.logger.error(f"Error fetching betting lines: {e}")
                raise

            # Convert to DataFrame, taking first provider's lines
            betting_data = []
            for game in lines:
                if game.lines and len(game.lines) > 0:
                    # Use first provider (usually consensus or main book)
                    line = game.lines[0]
                    betting_data.append({
                        'game_id': game.id,
                        'season': game.season,
                        'week': game.week,
                        'home_team': game.home_team,
                        'away_team': game.away_team,
                        'spread': line.spread if hasattr(line, 'spread') else None,
                        'formatted_spread': line.formatted_spread if hasattr(line, 'formatted_spread') else None,
                        'total': line.over_under if hasattr(line, 'over_under') else None,
                        'provider': line.provider if hasattr(line, 'provider') else None
                    })

            df = pd.DataFrame(betting_data)

            # Cache the results (only if not filtered by team)
            if not team and len(df) > 0:
                df.to_csv(cache_file, index=False)
                self.logger.info(f"Cached {len(df)} betting lines to {cache_file}")

            return df

    def clear_cache(self, year: Optional[int] = None):
        """
        Clear cached data

        Args:
            year: If specified, only clear cache for that year.
                  If None, clears all cache.
        """
        if year:
            pattern = f"*{year}*"
        else:
            pattern = "*"

        cleared = 0
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
            cleared += 1

        self.logger.info(f"Cleared {cleared} cached files")
        return cleared


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        client = CFBDClient()

        # Fetch teams
        print("\n=== Fetching Teams ===")
        teams = client.get_teams(2025)
        print(f"Fetched {len(teams)} FBS teams")
        print("\nSample teams:")
        print(teams[['name', 'conference', 'location']].head())

        # Fetch Week 1 schedule
        print("\n=== Fetching Week 1 Schedule ===")
        schedule = client.get_schedule(2025, week=1)
        print(f"Fetched {len(schedule)} Week 1 games")
        print("\nSample games:")
        print(schedule[['week', 'away_team', 'home_team', 'venue']].head())

        # Fetch Week 1 betting lines
        print("\n=== Fetching Week 1 Betting Lines ===")
        lines = client.get_betting_lines(2025, week=1)
        print(f"Fetched {len(lines)} betting lines")
        print("\nSample lines:")
        print(lines[['away_team', 'home_team', 'spread', 'total']].head())

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed cfbd: pip install cfbd")
        print("2. Set CFBD_API_KEY environment variable")
        print("3. Or created .env file with CFBD_API_KEY=your_key")
