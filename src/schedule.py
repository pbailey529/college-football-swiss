"""
Schedule data model for Swiss Tournament

Manages team schedules including Home/Away/Bye status for each week.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import pandas as pd
import logging


class TeamSchedule:
    """
    Manages schedule data for the Swiss tournament

    Attributes:
        schedule_df: DataFrame with columns [team, week, status, opponent, venue]
        season: Season year
        current_week: Current week number
    """

    def __init__(self, season: int = 2025):
        """
        Initialize TeamSchedule

        Args:
            season: Season year (e.g., 2025)
        """
        self.season = season
        self.current_week = 1
        self.schedule_df = None
        self.logger = logging.getLogger(__name__)

    def load_from_cfbd(self, games_df: pd.DataFrame, teams_df: pd.DataFrame):
        """
        Load schedule from CFBD games data

        Args:
            games_df: DataFrame from CFBD GamesApi.get_games()
            teams_df: DataFrame of teams to filter by

        Creates schedule_df with columns:
            - team: Team name
            - week: Week number
            - status: 'HOME', 'AWAY', or 'BYE'
            - opponent: Opponent name (None for BYE)
            - venue: Venue name (None for BYE)
            - swiss_opponent: Swiss tournament opponent (to be assigned)
        """
        team_names = set(teams_df['name'].values) if 'name' in teams_df.columns else set(teams_df.index)

        schedule_records = []

        # Process each week
        for week in range(1, 16):  # Weeks 1-15
            week_games = games_df[games_df['week'] == week]
            teams_this_week = set()

            # Process each game
            for _, game in week_games.iterrows():
                home_team = game['home_team']
                away_team = game['away_team']

                # Add home team
                if home_team in team_names:
                    schedule_records.append({
                        'team': home_team,
                        'week': week,
                        'status': 'HOME',
                        'opponent': away_team,
                        'venue': game.get('venue', None),
                        'game_id': game.get('game_id', None),
                        'swiss_opponent': None
                    })
                    teams_this_week.add(home_team)

                # Add away team
                if away_team in team_names:
                    schedule_records.append({
                        'team': away_team,
                        'week': week,
                        'status': 'AWAY',
                        'opponent': home_team,
                        'venue': game.get('venue', None),
                        'game_id': game.get('game_id', None),
                        'swiss_opponent': None
                    })
                    teams_this_week.add(away_team)

            # Add BYE weeks for teams not playing
            for team in team_names:
                if team not in teams_this_week:
                    schedule_records.append({
                        'team': team,
                        'week': week,
                        'status': 'BYE',
                        'opponent': None,
                        'venue': None,
                        'game_id': None,
                        'swiss_opponent': None
                    })

        self.schedule_df = pd.DataFrame(schedule_records)
        self.logger.info(f"Loaded schedule: {len(self.schedule_df)} team-week entries")

    def get_teams_by_status(self, week: int, status: str) -> List[str]:
        """
        Get teams with a specific status for a given week

        Args:
            week: Week number
            status: 'HOME', 'AWAY', or 'BYE'

        Returns:
            List of team names
        """
        if self.schedule_df is None:
            raise ValueError("Schedule not loaded. Call load_from_cfbd() first.")

        mask = (self.schedule_df['week'] == week) & (self.schedule_df['status'] == status)
        return self.schedule_df[mask]['team'].tolist()

    def get_home_teams(self, week: int) -> List[str]:
        """Get teams playing at home for a given week"""
        return self.get_teams_by_status(week, 'HOME')

    def get_away_teams(self, week: int) -> List[str]:
        """Get teams playing away for a given week"""
        return self.get_teams_by_status(week, 'AWAY')

    def get_bye_teams(self, week: int) -> List[str]:
        """Get teams on bye for a given week"""
        return self.get_teams_by_status(week, 'BYE')

    def get_team_status(self, team: str, week: int) -> Optional[str]:
        """
        Get a specific team's status for a given week

        Args:
            team: Team name
            week: Week number

        Returns:
            'HOME', 'AWAY', 'BYE', or None if not found
        """
        if self.schedule_df is None:
            return None

        mask = (self.schedule_df['team'] == team) & (self.schedule_df['week'] == week)
        result = self.schedule_df[mask]['status']

        return result.values[0] if len(result) > 0 else None

    def assign_swiss_pairing(self, team1: str, team2: str, week: int):
        """
        Assign Swiss tournament pairing for two teams

        Args:
            team1: First team name
            team2: Second team name
            week: Week number
        """
        if self.schedule_df is None:
            raise ValueError("Schedule not loaded.")

        # Update team1's swiss_opponent
        mask1 = (self.schedule_df['team'] == team1) & (self.schedule_df['week'] == week)
        self.schedule_df.loc[mask1, 'swiss_opponent'] = team2

        # Update team2's swiss_opponent
        mask2 = (self.schedule_df['team'] == team2) & (self.schedule_df['week'] == week)
        self.schedule_df.loc[mask2, 'swiss_opponent'] = team1

    def get_week_summary(self, week: int) -> Dict[str, int]:
        """
        Get summary statistics for a week

        Args:
            week: Week number

        Returns:
            Dict with counts of HOME, AWAY, and BYE teams
        """
        if self.schedule_df is None:
            return {'HOME': 0, 'AWAY': 0, 'BYE': 0}

        week_data = self.schedule_df[self.schedule_df['week'] == week]
        status_counts = week_data['status'].value_counts().to_dict()

        return {
            'HOME': status_counts.get('HOME', 0),
            'AWAY': status_counts.get('AWAY', 0),
            'BYE': status_counts.get('BYE', 0)
        }

    def save_to_csv(self, filepath: Path):
        """Save schedule to CSV file"""
        if self.schedule_df is not None:
            self.schedule_df.to_csv(filepath, index=False)
            self.logger.info(f"Saved schedule to {filepath}")

    def load_from_csv(self, filepath: Path):
        """Load schedule from CSV file"""
        self.schedule_df = pd.read_csv(filepath)
        self.logger.info(f"Loaded schedule from {filepath}")


def create_mock_schedule(teams: List[str], weeks: int = 15) -> TeamSchedule:
    """
    Create a mock schedule for testing (randomly assigns Home/Away/Bye)

    Args:
        teams: List of team names
        weeks: Number of weeks to generate

    Returns:
        TeamSchedule object with mock data
    """
    import random

    schedule = TeamSchedule()
    records = []

    for week in range(1, weeks + 1):
        # Randomly assign teams to home/away/bye
        shuffled_teams = teams.copy()
        random.shuffle(shuffled_teams)

        # Determine how many teams for each status
        n_teams = len(teams)
        n_bye = random.randint(0, min(4, n_teams // 10))  # 0-4 teams on bye
        n_playing = n_teams - n_bye
        n_home = n_playing // 2
        n_away = n_playing - n_home

        # Assign statuses
        for i, team in enumerate(shuffled_teams):
            if i < n_bye:
                status = 'BYE'
                opponent = None
            elif i < n_bye + n_home:
                status = 'HOME'
                # Pair with an away team
                away_idx = n_bye + n_home + (i - n_bye)
                opponent = shuffled_teams[away_idx] if away_idx < len(shuffled_teams) else None
            else:
                status = 'AWAY'
                # Pair with a home team
                home_idx = n_bye + (i - n_bye - n_home)
                opponent = shuffled_teams[home_idx] if home_idx < len(shuffled_teams) else None

            records.append({
                'team': team,
                'week': week,
                'status': status,
                'opponent': opponent,
                'venue': f"Stadium {i}" if status != 'BYE' else None,
                'game_id': None,
                'swiss_opponent': None
            })

    schedule.schedule_df = pd.DataFrame(records)
    return schedule


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Create mock schedule
    teams = ['Team A', 'Team B', 'Team C', 'Team D', 'Team E', 'Team F']
    schedule = create_mock_schedule(teams, weeks=3)

    # Test getting teams by status
    for week in range(1, 4):
        print(f"\n=== Week {week} ===")
        print(f"Home teams: {schedule.get_home_teams(week)}")
        print(f"Away teams: {schedule.get_away_teams(week)}")
        print(f"Bye teams: {schedule.get_bye_teams(week)}")
        print(f"Summary: {schedule.get_week_summary(week)}")
