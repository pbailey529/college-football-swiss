# Examples and Demonstrations

This directory contains example scripts demonstrating the College Football Swiss Tournament system.

## Available Examples

### `swiss_tournament_demo.py`
**Complete system demonstration** showing all major components:

- Schedule data model with Home/Away/Bye status
- Bipartite matching (Home vs Away constraint)
- Swiss scoring system (ATS, Style Points, Win Bonus)
- Full integration example

**Run it:**
```bash
# First install dependencies
pip install -r ../requirements.txt

# Then run demo
cd examples
python swiss_tournament_demo.py
```

**No API key required** - uses mock data for demonstration.

## Example Output

### Demo 1: Schedule Model
Shows how teams are tracked with Home/Away/Bye status for each week:
```
Week 1 Summary: 3 home, 3 away, 0 bye
Home teams: ['Alabama', 'Georgia', 'Ohio State']
Away teams: ['Michigan', 'Texas', 'USC']
```

### Demo 2: Bipartite Matching
Demonstrates Home/Away constraint in action:
```
Week 1 Swiss Pairings:
  Alabama (HOME) vs Michigan (AWAY)
  Georgia (HOME) vs Texas (AWAY)
  Ohio State (HOME) vs USC (AWAY)
```

### Demo 3: Swiss Scoring
Shows complete scoring breakdown:
```
Alabama (Favorite):
  ATS: +3.0 (won by 10, beat -7 spread by 3)
  Style Points: 2
    - Offensive: 1 (scored 30 > 28.25 projected)
    - Defensive: 1 (held to 20 < 21.75 projected)
  Win Bonus: 0
  TOTAL: 5.0 points

Swiss Tournament Winner: Alabama
```

## Future Examples

Additional examples to be added:

- `fetch_cfbd_data.py` - Fetching real 2025 data from CFBD API
- `simulate_week.py` - Simulating a complete week of the tournament
- `full_season_simulation.py` - Simulating an entire season
- `analyze_results.py` - Analyzing tournament results and statistics

## Requirements

For demos using mock data (like `swiss_tournament_demo.py`):
- No additional requirements

For examples using real data:
- CFBD API key (see main README.md)
- `cfbd` package installed: `pip install cfbd`
- `python-dotenv` for environment variables

## Contributing

To add a new example:
1. Create a descriptive Python file in this directory
2. Add clear docstrings explaining what it demonstrates
3. Include example output in comments or docstring
4. Update this README.md with the new example
