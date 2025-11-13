"""
Style Points Calculator

Rewards dominant offensive and defensive performance.
Based on Vegas-projected scores derived from spread and total.
"""

from typing import Tuple


def calculate_projected_scores(total: float, spread: float) -> Tuple[float, float]:
    """
    Calculate projected scores from Vegas total and spread

    Args:
        total: Over/Under total points
        spread: Point spread (negative = favorite)

    Returns:
        Tuple of (favorite_projected, underdog_projected)

    Formula:
        Favorite projected = (Total + |Spread|) / 2
        Underdog projected = (Total - |Spread|) / 2

    Examples:
        >>> calculate_projected_scores(50.0, -6.5)
        (28.25, 21.75)  # Favorite proj: 28.25, Underdog proj: 21.75

        >>> calculate_projected_scores(45.0, 3.0)
        (24.0, 21.0)  # Favorite proj: 24.0, Underdog proj: 21.0
    """
    spread_magnitude = abs(spread)

    favorite_projected = (total + spread_magnitude) / 2
    underdog_projected = (total - spread_magnitude) / 2

    return (favorite_projected, underdog_projected)


def calculate_style_points(
    team_score: int,
    opponent_score: int,
    team_projected: float,
    opponent_projected: float
) -> Tuple[int, int]:
    """
    Calculate style points for a team

    Awards:
    - Offensive style point: +1 if actual score > projected score
    - Defensive style point: +1 if opponent score < their projected score

    Args:
        team_score: Team's actual score
        opponent_score: Opponent's actual score
        team_projected: Team's Vegas-projected score
        opponent_projected: Opponent's Vegas-projected score

    Returns:
        Tuple of (offensive_style_point, defensive_style_point)
        Each is 0 or 1

    Examples:
        # Team scores 30 (projected 28.25), holds opponent to 20 (projected 21.75)
        >>> calculate_style_points(30, 20, 28.25, 21.75)
        (1, 1)  # Both offensive and defensive style points

        # Team scores 27 (projected 28.25), opponent scores 22 (projected 21.75)
        >>> calculate_style_points(27, 22, 28.25, 21.75)
        (0, 0)  # Neither threshold met

        # Team scores 29 (projected 28.25), opponent scores 22 (projected 21.75)
        >>> calculate_style_points(29, 22, 28.25, 21.75)
        (1, 0)  # Only offensive style point
    """
    # Offensive style point: score more than projected
    offensive_style = 1 if team_score > team_projected else 0

    # Defensive style point: hold opponent under their projection
    defensive_style = 1 if opponent_score < opponent_projected else 0

    return (offensive_style, defensive_style)


def calculate_style_points_from_vegas(
    team_a_score: int,
    team_b_score: int,
    total: float,
    spread: float
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Calculate style points for both teams from Vegas lines

    Args:
        team_a_score: Team A's score
        team_b_score: Team B's score
        total: Vegas Over/Under total
        spread: Point spread (negative = team A favored)

    Returns:
        Tuple of ((team_a_off, team_a_def), (team_b_off, team_b_def))
        Each inner tuple is (offensive_style, defensive_style)

    Examples:
        # Total: 50, Spread: -6.5 (A favored)
        # A scores 30 (proj 28.25), B scores 20 (proj 21.75)
        >>> calculate_style_points_from_vegas(30, 20, 50.0, -6.5)
        ((1, 1), (0, 0))
    """
    # Determine projections
    if spread < 0:
        # Team A is favorite
        team_a_proj, team_b_proj = calculate_projected_scores(total, spread)
    else:
        # Team B is favorite
        team_b_proj, team_a_proj = calculate_projected_scores(total, spread)

    # Calculate style points for each team
    team_a_style = calculate_style_points(team_a_score, team_b_score, team_a_proj, team_b_proj)
    team_b_style = calculate_style_points(team_b_score, team_a_score, team_b_proj, team_a_proj)

    return (team_a_style, team_b_style)


def total_style_points(offensive: int, defensive: int) -> int:
    """Sum offensive and defensive style points (0-2)"""
    return offensive + defensive


# Example usage and tests
if __name__ == "__main__":
    print("=== Style Points Calculator Examples ===\n")

    # Example from documentation
    print("Example: Total 50, Spread -6.5 (favorite wins 30-20)")
    total = 50.0
    spread = -6.5

    fav_proj, dog_proj = calculate_projected_scores(total, spread)
    print(f"  Favorite projected: {fav_proj:.2f} points")
    print(f"  Underdog projected: {dog_proj:.2f} points")
    print(f"  Favorite must score {int(fav_proj) + 1}+ for offensive style point")
    print(f"  Favorite must hold opponent under {int(dog_proj)} for defensive style point\n")

    # Favorite scores 30, opponent scores 20
    (team_a_style, team_b_style) = calculate_style_points_from_vegas(30, 20, total, spread)
    print(f"  Favorite actual: 30 points")
    print(f"  Underdog actual: 20 points")
    print(f"  Favorite style points: OFF={team_a_style[0]}, DEF={team_a_style[1]}, TOTAL={sum(team_a_style)}")
    print(f"  Underdog style points: OFF={team_b_style[0]}, DEF={team_b_style[1]}, TOTAL={sum(team_b_style)}\n")

    # Example 2: Close game
    print("Example 2: Total 45, Spread -3.0 (favorite wins 24-21)")
    (team_a_style, team_b_style) = calculate_style_points_from_vegas(24, 21, 45.0, -3.0)
    fav_proj, dog_proj = calculate_projected_scores(45.0, -3.0)
    print(f"  Projections: Fav {fav_proj:.1f}, Dog {dog_proj:.1f}")
    print(f"  Actual: Fav 24, Dog 21")
    print(f"  Favorite style: {sum(team_a_style)} (OFF={team_a_style[0]}, DEF={team_a_style[1]})")
    print(f"  Underdog style: {sum(team_b_style)} (OFF={team_b_style[0]}, DEF={team_b_style[1]})\n")
