"""
ATS (Against The Spread) Calculator

Calculates team performance against the Vegas spread.
This is the base metric for Swiss tournament scoring.
"""

from typing import Optional


def calculate_ats(
    team_score: int,
    opponent_score: int,
    spread: float,
    is_favorite: bool
) -> float:
    """
    Calculate ATS (Against The Spread) performance

    Formula: Actual Margin - Spread

    Args:
        team_score: Team's actual score
        opponent_score: Opponent's actual score
        spread: Vegas point spread (positive value)
        is_favorite: True if team is favored (spread is negative in original line)

    Returns:
        ATS performance (can be positive or negative)

    Examples:
        # Team favored by 7, wins by 10
        >>> calculate_ats(30, 20, 7, is_favorite=True)
        3.0  # Beat spread by 3

        # Team underdog by 3, loses by 1
        >>> calculate_ats(20, 21, 3, is_favorite=False)
        2.0  # Beat spread by 2

        # Team favored by 7, wins by 3
        >>> calculate_ats(24, 21, 7, is_favorite=True)
        -4.0  # Lost to spread by 4
    """
    actual_margin = team_score - opponent_score

    if is_favorite:
        # Favorite: ATS = Actual Margin - Spread
        # Need to win by more than spread to beat it
        ats = actual_margin - spread
    else:
        # Underdog: ATS = Actual Margin + Spread
        # Can lose by less than spread and still beat it
        ats = actual_margin + spread

    return ats


def determine_favorite(spread: float) -> tuple[bool, bool]:
    """
    Determine which team is favored based on spread

    Args:
        spread: Point spread (negative for team A favored, positive for team B favored)

    Returns:
        Tuple of (team_a_is_favorite, team_b_is_favorite)

    Examples:
        >>> determine_favorite(-7.0)
        (True, False)  # Team A favored by 7

        >>> determine_favorite(3.5)
        (False, True)  # Team B favored by 3.5
    """
    if spread < 0:
        return (True, False)
    elif spread > 0:
        return (False, True)
    else:
        return (False, False)  # Pick'em


def calculate_ats_from_spread(
    team_a_score: int,
    team_b_score: int,
    spread: float
) -> tuple[float, float]:
    """
    Calculate ATS for both teams given a spread line

    Convention: Negative spread means team A is favored

    Args:
        team_a_score: Team A's score
        team_b_score: Team B's score
        spread: Point spread (negative = team A favored)

    Returns:
        Tuple of (team_a_ats, team_b_ats)

    Examples:
        # Team A favored by 7 (-7), wins by 10
        >>> calculate_ats_from_spread(30, 20, -7.0)
        (3.0, -3.0)

        # Team B favored by 3 (+3 from team A's perspective), loses by 1
        >>> calculate_ats_from_spread(21, 20, 3.0)
        (-2.0, 2.0)
    """
    team_a_is_fav, team_b_is_fav = determine_favorite(spread)
    spread_magnitude = abs(spread)

    team_a_ats = calculate_ats(team_a_score, team_b_score, spread_magnitude, team_a_is_fav)
    team_b_ats = calculate_ats(team_b_score, team_a_score, spread_magnitude, team_b_is_fav)

    return (team_a_ats, team_b_ats)


# Example usage and tests
if __name__ == "__main__":
    print("=== ATS Calculator Examples ===\n")

    # Example 1: Favorite beats spread
    print("Example 1: Team favored by 7, wins by 10")
    ats = calculate_ats(30, 20, 7, is_favorite=True)
    print(f"  ATS: {ats:+.1f} (beat spread by 3)\n")

    # Example 2: Underdog beats spread
    print("Example 2: Team underdog by 3, loses by 1")
    ats = calculate_ats(20, 21, 3, is_favorite=False)
    print(f"  ATS: {ats:+.1f} (beat spread by 2)\n")

    # Example 3: Favorite fails to cover
    print("Example 3: Team favored by 7, wins by 3")
    ats = calculate_ats(24, 21, 7, is_favorite=True)
    print(f"  ATS: {ats:+.1f} (lost to spread by 4)\n")

    # Example 4: Using spread directly
    print("Example 4: Team A favored by 7 (-7), wins by 10 (30-20)")
    team_a_ats, team_b_ats = calculate_ats_from_spread(30, 20, -7.0)
    print(f"  Team A ATS: {team_a_ats:+.1f}")
    print(f"  Team B ATS: {team_b_ats:+.1f}\n")
