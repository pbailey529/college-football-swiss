"""
Export college football Swiss tournament data to GeoJSON format for web visualization.
"""
import json
from pathlib import Path
import pandas as pd
from tournament import Tournament


def export_teams_geojson(teams_df: pd.DataFrame, output_path: str):
    """
    Export team locations to GeoJSON Point features.

    Args:
        teams_df: DataFrame with team data including lat, long, rating
        output_path: Path to save the GeoJSON file
    """
    features = []

    for idx, row in teams_df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['long'], row['lat']]  # GeoJSON uses [lon, lat]
            },
            "properties": {
                "nickname": idx,  # idx is the nickname (index column)
                "team": row['team'],
                "conference": row['conference'],
                "rating": float(row['rating']),
                "wins": str(row.get('wins', '')),
                "losses": str(row.get('losses', '')),
                "score": int(row.get('score', 0))
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"Exported {len(features)} teams to {output_path}")


def export_matchups_geojson(pairings: set, teams_df: pd.DataFrame, output_path: str, round_num: int = 1):
    """
    Export matchups to GeoJSON LineString features.

    Args:
        pairings: Set of (team_a, team_b) tuples from tournament
        teams_df: DataFrame with team data
        output_path: Path to save the GeoJSON file
        round_num: Current round number
    """
    features = []

    for team_a_id, team_b_id in pairings:
        team_a = teams_df.loc[team_a_id]
        team_b = teams_df.loc[team_b_id]

        # Calculate matchup competitiveness (closer to 0 = more evenly matched)
        rating_diff = abs(team_a['rating'] - team_b['rating'])

        # Determine if this is a "top matchup" (both teams highly rated)
        avg_rating = (team_a['rating'] + team_b['rating']) / 2
        is_top_matchup = avg_rating >= 75  # Threshold for "top teams"

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [team_a['long'], team_a['lat']],
                    [team_b['long'], team_b['lat']]
                ]
            },
            "properties": {
                "round": round_num,
                "team_a_nickname": team_a_id,  # team_a_id is the nickname (index)
                "team_a_name": team_a['team'],
                "team_a_rating": float(team_a['rating']),
                "team_a_record": f"{int(team_a.get('score', 0))}-{len(str(team_a.get('losses', '')).split()) if team_a.get('losses', '') else 0}",
                "team_b_nickname": team_b_id,  # team_b_id is the nickname (index)
                "team_b_name": team_b['team'],
                "team_b_rating": float(team_b['rating']),
                "team_b_record": f"{int(team_b.get('score', 0))}-{len(str(team_b.get('losses', '')).split()) if team_b.get('losses', '') else 0}",
                "rating_diff": float(rating_diff),
                "avg_rating": float(avg_rating),
                "is_top_matchup": bool(is_top_matchup),
                "distance_miles": calculate_distance(team_a['lat'], team_a['long'],
                                                     team_b['lat'], team_b['long'])
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)

    print(f"Exported {len(features)} matchups to {output_path}")


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate great circle distance between two points in miles."""
    from math import radians, sin, cos, sqrt, atan2

    R = 3959  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return round(distance, 1)


def export_tournament_round(round_num: int = 1):
    """
    Generate and export a complete tournament round (teams + matchups).

    Args:
        round_num: Round number to generate (1-12)
    """
    base_path = Path(__file__).parent.parent
    input_path = base_path / "input" / "cfb_teams.csv"
    output_dir = base_path / "web" / "data"
    output_dir.mkdir(exist_ok=True)

    # Load teams
    teams_df = pd.read_csv(input_path, index_col='nickname')
    teams_df['score'] = 0
    teams_df['wins'] = ''
    teams_df['losses'] = ''

    # Initialize tournament
    tournament = Tournament(teams_df)

    # Simulate rounds up to target round
    for _ in range(round_num):
        tournament.simulate_round()
        tournament.update_distances()

    # Export current state
    teams_output = output_dir / f"teams_round{round_num}.geojson"
    export_teams_geojson(tournament.teams_df, teams_output)

    # Get next round's pairings
    next_pairings = tournament.get_pairings()
    matchups_output = output_dir / f"matchups_round{round_num + 1}.geojson"
    export_matchups_geojson(next_pairings, tournament.teams_df, matchups_output, round_num + 1)

    print(f"\n✅ Round {round_num} data exported successfully!")
    print(f"   - Teams: {teams_output}")
    print(f"   - Next matchups: {matchups_output}")


if __name__ == "__main__":
    # Export Week 1 matchups (before any games have been played)
    print("Generating Week 1 College Football Swiss matchups...\n")
    export_tournament_round(round_num=0)

    # Also export Week 2 after simulating Week 1
    print("\n" + "="*60)
    print("Generating Week 2 matchups (after Week 1 results)...\n")
    export_tournament_round(round_num=1)
