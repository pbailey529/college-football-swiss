"""
Swiss Tournament Demonstration

Shows how all components work together:
- CFP team filtering
- Schedule data with Home/Away constraints
- Bipartite matching
- Swiss scoring system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pandas as pd
import logging
from schedule import TeamSchedule, create_mock_schedule
from tournament import Tournament
from swiss import get_cfp_eligible_teams
from scoring import SwissScorer, GameResult

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def demo_schedule_model():
    """Demonstrate schedule data model"""
    print("\n" + "=" * 60)
    print("DEMO 1: Schedule Data Model with Home/Away/Bye Status")
    print("=" * 60 + "\n")

    # Create mock schedule for demo teams
    teams = ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Texas', 'USC']
    schedule = create_mock_schedule(teams, weeks=3)

    # Show schedule for each week
    for week in range(1, 4):
        print(f"\n--- Week {week} ---")
        summary = schedule.get_week_summary(week)
        print(f"Summary: {summary['HOME']} home, {summary['AWAY']} away, {summary['BYE']} bye")

        print(f"Home teams: {schedule.get_home_teams(week)}")
        print(f"Away teams: {schedule.get_away_teams(week)}")
        print(f"Bye teams: {schedule.get_bye_teams(week)}")


def demo_bipartite_matching():
    """Demonstrate Home/Away bipartite matching"""
    print("\n" + "=" * 60)
    print("DEMO 2: Bipartite Matching (Home vs Away Only)")
    print("=" * 60 + "\n")

    # Create sample teams DataFrame
    teams_data = {
        'team': ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Texas', 'USC', 'Oregon', 'LSU'],
        'coords': [
            '(32.3, -86.9)', '(33.9, -83.4)', '(40.0, -83.0)', '(42.3, -83.7)',
            '(30.3, -97.7)', '(34.0, -118.3)', '(44.0, -123.1)', '(30.4, -91.2)'
        ],
        'rating': [95, 94, 93, 91, 92, 89, 90, 87],
        'conference': ['SEC', 'SEC', 'BIG TEN', 'BIG TEN', 'SEC', 'BIG TEN', 'BIG TEN', 'SEC'],
        'score': [0, 0, 0, 0, 0, 0, 0, 0],
        'wins': ['', '', '', '', '', '', '', ''],
        'losses': ['', '', '', '', '', '', '', '']
    }
    teams_df = pd.DataFrame(teams_data)
    teams_df = teams_df.set_index('team')

    # Create mock schedule
    teams_list = teams_df.index.tolist()
    schedule = create_mock_schedule(teams_list, weeks=2)

    # Show Week 1 matchings
    week = 1
    print(f"Week {week} Status:")
    print(f"  Home teams: {schedule.get_home_teams(week)}")
    print(f"  Away teams: {schedule.get_away_teams(week)}")
    print(f"  Bye teams: {schedule.get_bye_teams(week)}")

    # Create tournament with Home/Away constraint
    print("\nCreating tournament with Home/Away constraint...")
    tournament = Tournament(
        teams_df=teams_df,
        schedule=schedule,
        use_home_away_constraint=True
    )

    # Get pairings
    print("\nGenerating pairings...")
    pairings = tournament.get_pairings()

    print(f"\nWeek {week} Swiss Pairings:")
    for team1, team2 in pairings:
        team1_status = schedule.get_team_status(team1, week)
        team2_status = schedule.get_team_status(team2, week)
        print(f"  {team1} ({team1_status}) vs {team2} ({team2_status})")

    print("\n✓ All pairings respect Home/Away constraint!")


def demo_swiss_scoring():
    """Demonstrate Swiss scoring system"""
    print("\n" + "=" * 60)
    print("DEMO 3: Swiss Tournament Scoring System")
    print("=" * 60 + "\n")

    # Example game from documentation
    print("Game: Alabama vs Georgia")
    print("  Vegas Line: Alabama -7, Total: 50")
    print("  Final Score: Alabama 30, Georgia 20")
    print("  Georgia's opponent has 2 P4 wins\n")

    game = GameResult(
        team_a="Alabama",
        team_b="Georgia",
        team_a_score=30,
        team_b_score=20,
        spread=-7.0,
        total=50.0,
        team_a_opponent_p4_wins=0,
        team_b_opponent_p4_wins=2
    )

    scorer = SwissScorer()
    alabama_score, georgia_score = scorer.score_game(game)

    print("Alabama (Favorite):")
    print(f"  ATS: {alabama_score.ats:+.1f} (won by 10, beat -7 spread by 3)")
    print(f"  Style Points: {alabama_score.style_total}")
    print(f"    - Offensive: {alabama_score.offensive_style} (scored 30 > 28.25 projected)")
    print(f"    - Defensive: {alabama_score.defensive_style} (held to 20 < 21.75 projected)")
    print(f"  Win Bonus: {alabama_score.win_bonus} (Georgia has 0 P4 wins)")
    print(f"  TOTAL: {alabama_score.total_score:.1f} points\n")

    print("Georgia (Underdog):")
    print(f"  ATS: {georgia_score.ats:+.1f} (lost by 10, did not beat +7 spread)")
    print(f"  Style Points: {georgia_score.style_total}")
    print(f"    - Offensive: {georgia_score.offensive_style}")
    print(f"    - Defensive: {georgia_score.defensive_style}")
    print(f"  Win Bonus: {georgia_score.win_bonus} (no bonus for losing)")
    print(f"  TOTAL: {georgia_score.total_score:.1f} points\n")

    winner = scorer.determine_swiss_winner(alabama_score, georgia_score)
    print(f"Swiss Tournament Winner: {winner}")
    print(f"Alabama wins the Swiss matchup with {alabama_score.total_score:.1f} points!")


def demo_full_integration():
    """Demonstrate full system integration"""
    print("\n" + "=" * 60)
    print("DEMO 4: Full System Integration")
    print("=" * 60 + "\n")

    print("This would demonstrate:")
    print("1. Loading CFP-eligible teams from CFBD API")
    print("2. Loading schedule data for 2025 season")
    print("3. Generating Week 1 pairings with Home/Away constraint")
    print("4. Simulating real game results")
    print("5. Calculating Swiss scores")
    print("6. Determining Swiss matchup winners")
    print("7. Updating tournament standings")
    print("\nNote: Requires CFBD API key. See examples/full_integration_example.py")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("COLLEGE FOOTBALL SWISS TOURNAMENT - DEMONSTRATION")
    print("=" * 60)

    try:
        demo_schedule_model()
        demo_bipartite_matching()
        demo_swiss_scoring()
        demo_full_integration()

        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback
        traceback.print_exc()
