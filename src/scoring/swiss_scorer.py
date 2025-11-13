"""
Swiss Tournament Scorer

Combines ATS, Style Points, and Win Bonus to calculate total Swiss score.
Determines winner of Swiss tournament matchup.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import pandas as pd

from .ats_calculator import calculate_ats_from_spread
from .style_points import calculate_style_points_from_vegas, total_style_points
from .win_bonus import calculate_win_bonus


@dataclass
class GameResult:
    """
    Represents the result of a real game

    Attributes:
        team_a: Team A name
        team_b: Team B name
        team_a_score: Team A final score
        team_b_score: Team B final score
        spread: Vegas point spread (negative = team A favored)
        total: Vegas Over/Under total
        team_a_opponent_p4_wins: Number of P4 wins by team A's opponent
        team_b_opponent_p4_wins: Number of P4 wins by team B's opponent
    """
    team_a: str
    team_b: str
    team_a_score: int
    team_b_score: int
    spread: float
    total: float
    team_a_opponent_p4_wins: int = 0
    team_b_opponent_p4_wins: int = 0


@dataclass
class SwissScore:
    """
    Swiss tournament score breakdown for a team

    Attributes:
        team: Team name
        ats: ATS performance
        offensive_style: Offensive style point (0 or 1)
        defensive_style: Defensive style point (0 or 1)
        style_total: Total style points (0-2)
        win_bonus: Win bonus points (0+)
        total_score: Total Swiss score
        won_game: True if team won their real game
    """
    team: str
    ats: float
    offensive_style: int
    defensive_style: int
    style_total: int
    win_bonus: int
    total_score: float
    won_game: bool

    def __str__(self):
        return (
            f"{self.team}: {self.total_score:.2f} pts "
            f"(ATS: {self.ats:+.1f}, Style: {self.style_total}, "
            f"Bonus: {self.win_bonus})"
        )


def calculate_swiss_score(
    team_score: int,
    opponent_score: int,
    spread: float,
    total: float,
    is_favorite: bool,
    opponent_p4_wins: int = 0
) -> SwissScore:
    """
    Calculate Swiss tournament score for a team

    Args:
        team_score: Team's score
        opponent_score: Opponent's score
        spread: Point spread magnitude (positive value)
        total: Vegas Over/Under total
        is_favorite: True if team is favored
        opponent_p4_wins: Number of P4 wins by opponent

    Returns:
        SwissScore object with breakdown
    """
    from .ats_calculator import calculate_ats
    from .style_points import calculate_projected_scores, calculate_style_points

    # Determine if team won
    team_won = team_score > opponent_score

    # Calculate ATS
    ats = calculate_ats(team_score, opponent_score, spread, is_favorite)

    # Calculate projections and style points
    if is_favorite:
        team_proj, opp_proj = calculate_projected_scores(total, spread)
    else:
        opp_proj, team_proj = calculate_projected_scores(total, spread)

    off_style, def_style = calculate_style_points(
        team_score, opponent_score, team_proj, opp_proj
    )

    # Calculate win bonus
    win_bonus = calculate_win_bonus(team_won, "opponent", opponent_p4_wins)

    # Total score
    total_score = ats + off_style + def_style + win_bonus

    return SwissScore(
        team="team",
        ats=ats,
        offensive_style=off_style,
        defensive_style=def_style,
        style_total=off_style + def_style,
        win_bonus=win_bonus,
        total_score=total_score,
        won_game=team_won
    )


class SwissScorer:
    """
    Swiss Tournament Scorer

    Calculates Swiss scores for matchups and determines winners.
    """

    def __init__(self, p4_wins_dict: Optional[Dict[str, int]] = None):
        """
        Initialize Swiss Scorer

        Args:
            p4_wins_dict: Optional dict mapping team names to P4 wins count
        """
        self.p4_wins_dict = p4_wins_dict or {}

    def score_game(self, game: GameResult) -> Tuple[SwissScore, SwissScore]:
        """
        Score a game for both teams

        Args:
            game: GameResult object

        Returns:
            Tuple of (team_a_score, team_b_score)
        """
        # Calculate ATS for both teams
        team_a_ats, team_b_ats = calculate_ats_from_spread(
            game.team_a_score,
            game.team_b_score,
            game.spread
        )

        # Calculate style points for both teams
        team_a_style, team_b_style = calculate_style_points_from_vegas(
            game.team_a_score,
            game.team_b_score,
            game.total,
            game.spread
        )

        # Determine winners
        team_a_won = game.team_a_score > game.team_b_score
        team_b_won = game.team_b_score > game.team_a_score

        # Calculate win bonuses
        team_a_bonus = calculate_win_bonus(
            team_a_won,
            game.team_b,
            game.team_a_opponent_p4_wins
        )
        team_b_bonus = calculate_win_bonus(
            team_b_won,
            game.team_a,
            game.team_b_opponent_p4_wins
        )

        # Create SwissScore objects
        team_a_score_obj = SwissScore(
            team=game.team_a,
            ats=team_a_ats,
            offensive_style=team_a_style[0],
            defensive_style=team_a_style[1],
            style_total=sum(team_a_style),
            win_bonus=team_a_bonus,
            total_score=team_a_ats + sum(team_a_style) + team_a_bonus,
            won_game=team_a_won
        )

        team_b_score_obj = SwissScore(
            team=game.team_b,
            ats=team_b_ats,
            offensive_style=team_b_style[0],
            defensive_style=team_b_style[1],
            style_total=sum(team_b_style),
            win_bonus=team_b_bonus,
            total_score=team_b_ats + sum(team_b_style) + team_b_bonus,
            won_game=team_b_won
        )

        return (team_a_score_obj, team_b_score_obj)

    def determine_swiss_winner(
        self,
        team_a_score: SwissScore,
        team_b_score: SwissScore,
        team_a_avg_ats: float = 0.0,
        team_b_avg_ats: float = 0.0
    ) -> str:
        """
        Determine winner of Swiss tournament matchup

        Tiebreaker: Season average ATS performance

        Args:
            team_a_score: Team A's Swiss score
            team_b_score: Team B's Swiss score
            team_a_avg_ats: Team A's season average ATS (tiebreaker)
            team_b_avg_ats: Team B's season average ATS (tiebreaker)

        Returns:
            Name of winning team
        """
        if team_a_score.total_score > team_b_score.total_score:
            return team_a_score.team
        elif team_b_score.total_score > team_a_score.total_score:
            return team_b_score.team
        else:
            # Tiebreaker: Season average ATS
            if team_a_avg_ats > team_b_avg_ats:
                return team_a_score.team
            elif team_b_avg_ats > team_a_avg_ats:
                return team_b_score.team
            else:
                # Still tied, arbitrary winner
                return team_a_score.team


# Example usage
if __name__ == "__main__":
    print("=== Swiss Scorer Examples ===\n")

    # Example from documentation
    print("Example: Team A favored by 7, wins 30-20")
    print("  Total: 50, Opponent has 2 P4 wins\n")

    game = GameResult(
        team_a="Team A",
        team_b="Team B",
        team_a_score=30,
        team_b_score=20,
        spread=-7.0,
        total=50.0,
        team_a_opponent_p4_wins=0,
        team_b_opponent_p4_wins=2  # Team B's opponent (Team A) has 2 P4 wins
    )

    scorer = SwissScorer()
    team_a_score, team_b_score = scorer.score_game(game)

    print("Team A (Favorite):")
    print(f"  ATS: {team_a_score.ats:+.1f}")
    print(f"  Style Points: {team_a_score.style_total} (OFF: {team_a_score.offensive_style}, DEF: {team_a_score.defensive_style})")
    print(f"  Win Bonus: {team_a_score.win_bonus}")
    print(f"  TOTAL: {team_a_score.total_score:.1f}\n")

    print("Team B (Underdog):")
    print(f"  ATS: {team_b_score.ats:+.1f}")
    print(f"  Style Points: {team_b_score.style_total} (OFF: {team_b_score.offensive_style}, DEF: {team_b_score.defensive_style})")
    print(f"  Win Bonus: {team_b_score.win_bonus}")
    print(f"  TOTAL: {team_b_score.total_score:.1f}\n")

    winner = scorer.determine_swiss_winner(team_a_score, team_b_score)
    print(f"Swiss Tournament Winner: {winner}\n")

    # Another example: Close game
    print("=" * 50)
    print("\nExample 2: Close upset - Underdog wins 24-21")
    print("  Total: 45, Spread: -3.0 (Team A favored)\n")

    game2 = GameResult(
        team_a="Georgia",
        team_b="Florida",
        team_a_score=21,
        team_b_score=24,
        spread=-3.0,
        total=45.0,
        team_a_opponent_p4_wins=1,
        team_b_opponent_p4_wins=3
    )

    team_a_score2, team_b_score2 = scorer.score_game(game2)

    print(f"{team_a_score2}")
    print(f"{team_b_score2}\n")

    winner2 = scorer.determine_swiss_winner(team_a_score2, team_b_score2)
    print(f"Swiss Tournament Winner: {winner2}")
