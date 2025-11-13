"""
Win Bonus Calculator

Rewards teams for beating quality opponents.
Bonus = Number of P4 conference wins by the team's real opponent.
Only awarded if the team WINS their game.
"""

from typing import Dict, Optional
import pandas as pd


# P4 Conferences (2025 season)
P4_CONFERENCES = {
    'BIG TEN',
    'SEC',
    'ACC',
    'BIG 12'
}


def is_p4_team(conference: str) -> bool:
    """
    Check if a team is in a P4 conference

    Args:
        conference: Conference name

    Returns:
        True if team is in P4 conference
    """
    return conference.upper() in P4_CONFERENCES


def calculate_win_bonus(
    team_won: bool,
    opponent_name: str,
    opponent_p4_wins: int
) -> int:
    """
    Calculate win bonus for a team

    Formula:
    - If team WON: Bonus = Opponent's P4 wins
    - If team LOST: Bonus = 0

    Args:
        team_won: True if team won their game
        opponent_name: Name of opponent (for reference)
        opponent_p4_wins: Number of P4 conference wins by opponent

    Returns:
        Win bonus points (0 or more)

    Examples:
        # Beat Tennessee who has 2 P4 wins
        >>> calculate_win_bonus(True, "Tennessee", 2)
        2

        # Lost to Alabama who has 5 P4 wins
        >>> calculate_win_bonus(False, "Alabama", 5)
        0

        # Beat weak opponent with 0 P4 wins
        >>> calculate_win_bonus(True, "FCS Team", 0)
        0
    """
    if not team_won:
        return 0

    return opponent_p4_wins


def count_p4_wins(
    team_results: pd.DataFrame,
    teams_df: pd.DataFrame
) -> Dict[str, int]:
    """
    Count P4 wins for all teams

    Args:
        team_results: DataFrame with columns [team, opponent, team_won, week]
        teams_df: DataFrame with team info including 'conference' column

    Returns:
        Dict mapping team name to P4 wins count

    Example:
        >>> results = pd.DataFrame({
        ...     'team': ['Alabama', 'Alabama', 'Georgia'],
        ...     'opponent': ['Tennessee', 'LSU', 'Auburn'],
        ...     'team_won': [True, True, True]
        ... })
        >>> teams = pd.DataFrame({
        ...     'name': ['Alabama', 'Tennessee', 'LSU', 'Auburn', 'Georgia'],
        ...     'conference': ['SEC', 'SEC', 'SEC', 'SEC', 'SEC']
        ... }, index=['Alabama', 'Tennessee', 'LSU', 'Auburn', 'Georgia'])
        >>> count_p4_wins(results, teams)
        {'Alabama': 2, 'Georgia': 1, ...}
    """
    # Create conference lookup
    conference_map = {}
    if 'name' in teams_df.columns:
        conference_map = dict(zip(teams_df['name'], teams_df['conference']))
    else:
        conference_map = dict(zip(teams_df.index, teams_df['conference']))

    # Count P4 wins for each team
    p4_wins = {}

    for team in team_results['team'].unique():
        team_games = team_results[team_results['team'] == team]
        wins = 0

        for _, game in team_games.iterrows():
            if game['team_won']:
                opponent = game['opponent']
                opponent_conf = conference_map.get(opponent, '')

                if is_p4_team(opponent_conf):
                    wins += 1

        p4_wins[team] = wins

    return p4_wins


def get_opponent_p4_wins(
    opponent_name: str,
    p4_wins_dict: Dict[str, int]
) -> int:
    """
    Get P4 wins for an opponent

    Args:
        opponent_name: Name of opponent
        p4_wins_dict: Dict mapping team names to P4 wins

    Returns:
        Number of P4 wins (0 if not found)
    """
    return p4_wins_dict.get(opponent_name, 0)


# Example usage and tests
if __name__ == "__main__":
    print("=== Win Bonus Calculator Examples ===\n")

    # Example 1: Beat strong opponent
    print("Example 1: Beat Tennessee (who has 2 P4 wins)")
    bonus = calculate_win_bonus(True, "Tennessee", 2)
    print(f"  Win Bonus: {bonus} points\n")

    # Example 2: Lost to strong opponent
    print("Example 2: Lost to Alabama (who has 5 P4 wins)")
    bonus = calculate_win_bonus(False, "Alabama", 5)
    print(f"  Win Bonus: {bonus} points (no bonus for losing)\n")

    # Example 3: Beat weak opponent
    print("Example 3: Beat team with 0 P4 wins")
    bonus = calculate_win_bonus(True, "Weak Opponent", 0)
    print(f"  Win Bonus: {bonus} points\n")

    # Example 4: Test P4 conference checking
    print("Example 4: P4 Conference Checking")
    for conf in ['SEC', 'Big Ten', 'ACC', 'Big 12', 'AAC', 'MAC']:
        is_p4 = is_p4_team(conf)
        print(f"  {conf}: {'P4' if is_p4 else 'Not P4'}")
    print()

    # Example 5: Count P4 wins from sample data
    print("Example 5: Counting P4 Wins")
    results = pd.DataFrame({
        'team': ['Alabama', 'Alabama', 'Alabama', 'Georgia', 'Georgia'],
        'opponent': ['Tennessee', 'LSU', 'Auburn', 'Florida', 'Vanderbilt'],
        'team_won': [True, True, False, True, True]
    })

    teams = pd.DataFrame({
        'name': ['Alabama', 'Tennessee', 'LSU', 'Auburn', 'Georgia', 'Florida', 'Vanderbilt'],
        'conference': ['SEC', 'SEC', 'SEC', 'SEC', 'SEC', 'SEC', 'SEC']
    })

    p4_wins = count_p4_wins(results, teams)
    print("  P4 Wins by team:")
    for team, wins in p4_wins.items():
        print(f"    {team}: {wins} P4 wins")
