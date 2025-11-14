# Data Sources for College Football Swiss Tournament

## Selected Solution: CollegeFootballData.com (CFBD) API

**Recommendation**: Use the **CFBD API** for both betting lines and schedule data. This provides a unified, well-documented, and actively maintained data source.

---

## Why CFBD API?

### Advantages
1. **Comprehensive Coverage**: Single API for betting lines, schedules, team data, and game results
2. **Well-Documented**: Extensive documentation and Python wrapper available
3. **Active Maintenance**: Regular updates, supports 2025 season data
4. **Free Tier Available**: 1,000 API calls/month (sufficient for initial development)
5. **Python Integration**: Official `cfbd-python` library with pip installation
6. **Structured Data**: Clean JSON responses with consistent schema
7. **Flexible Filtering**: Filter by year, week, team, conference, home/away, etc.
8. **Historical Data**: Access to historical betting lines and game results

### Limitations
- **Rate Limits**: Free tier limited to 1,000 calls/month (Patreon tiers offer more)
- **API Key Required**: Must register at collegefootballdata.com
- **Dependency**: Relies on third-party service availability

---

## CFBD API Endpoints

### 1. Betting Lines Endpoint

#### BettingApi.get_lines()

**Purpose**: Retrieve closing betting lines (spreads and totals) for games

**Parameters**:
```python
{
    "year": int,              # Required: Season year (e.g., 2025)
    "week": int,              # Optional: Week number (1-15)
    "season_type": str,       # Optional: "regular" or "postseason" (default: "regular")
    "team": str,              # Optional: Team name filter
    "home": str,              # Optional: Home team filter
    "away": str,              # Optional: Away team filter
    "conference": str,        # Optional: Conference abbreviation
    "game_id": int            # Optional: Specific game ID
}
```

**Returns**: `list[GameLines]`

**Data Fields** (GameLines object):
- `id`: Game ID
- `season`: Season year
- `week`: Week number
- `season_type`: "regular" or "postseason"
- `start_date`: Game date/time
- `home_team`: Home team name
- `away_team`: Away team name
- `lines`: List of betting lines from various providers
  - `provider`: Sportsbook name
  - `spread`: Point spread (negative for favorite)
  - `formatted_spread`: Human-readable spread (e.g., "-7.5")
  - `over_under`: Total points O/U
  - Additional metadata

**Example Usage**:
```python
import cfbd

# Configure API client
configuration = cfbd.Configuration()
configuration.access_token = 'YOUR_API_KEY'

with cfbd.ApiClient(configuration) as api_client:
    betting_api = cfbd.BettingApi(api_client)

    # Get Week 1 betting lines for 2025
    lines = betting_api.get_lines(year=2025, week=1, season_type='regular')

    for game in lines:
        print(f"{game.away_team} @ {game.home_team}")
        if game.lines:
            line = game.lines[0]  # First provider
            print(f"  Spread: {line.formatted_spread}")
            print(f"  Total: {line.over_under}")
```

---

### 2. Games/Schedule Endpoint

#### GamesApi.get_games()

**Purpose**: Retrieve game schedules and results

**Parameters**:
```python
{
    "year": int,              # Required: Season year (e.g., 2025)
    "week": int,              # Optional: Week number
    "season_type": str,       # Optional: "regular" or "postseason"
    "team": str,              # Optional: Team name filter
    "home": str,              # Optional: Home team filter
    "away": str,              # Optional: Away team filter
    "conference": str,        # Optional: Conference abbreviation
    "division": str,          # Optional: "fbs", "fcs", "ii", "iii"
    "id": int                 # Optional: Specific game ID
}
```

**Returns**: `list[Game]`

**Data Fields** (Game object):
- `id`: Game ID
- `season`: Season year
- `week`: Week number
- `season_type`: "regular" or "postseason"
- `start_date`: Game date/time
- `start_time_tbd`: Boolean if time not set
- `neutral_site`: Boolean if neutral site
- `conference_game`: Boolean if conference game
- `home_team`: Home team name
- `home_conference`: Home team conference
- `home_points`: Home team score (if completed)
- `away_team`: Away team name
- `away_conference`: Away team conference
- `away_points`: Away team score (if completed)
- `venue`: Stadium name
- `venue_id`: Venue ID
- `home_line_scores`: Quarter-by-quarter scores (home)
- `away_line_scores`: Quarter-by-quarter scores (away)

**Example Usage**:
```python
import cfbd

configuration = cfbd.Configuration()
configuration.access_token = 'YOUR_API_KEY'

with cfbd.ApiClient(configuration) as api_client:
    games_api = cfbd.GamesApi(api_client)

    # Get all games for Week 1, 2025
    games = games_api.get_games(year=2025, week=1)

    for game in games:
        location = "vs" if game.neutral_site else "@"
        print(f"{game.away_team} {location} {game.home_team}")
        print(f"  Venue: {game.venue}")
        print(f"  Date: {game.start_date}")
        if game.home_points is not None:
            print(f"  Score: {game.away_points}-{game.home_points}")
```

---

### 3. Teams Endpoint

#### TeamsApi.get_teams()

**Purpose**: Retrieve team information and metadata

**Parameters**:
```python
{
    "conference": str,        # Optional: Conference abbreviation
    "year": int              # Optional: Season year
}
```

**Returns**: `list[Team]`

**Data Fields**:
- `id`: Team ID
- `school`: Team name
- `mascot`: Team mascot
- `abbreviation`: Team abbreviation
- `alt_name_1`, `alt_name_2`, `alt_name_3`: Alternative names
- `conference`: Conference name
- `division`: "fbs", "fcs", etc.
- `color`: Primary color hex code
- `alt_color`: Secondary color hex code
- `logos`: List of logo URLs
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `location`: City, State

**Example Usage**:
```python
teams_api = cfbd.TeamsApi(api_client)
fbs_teams = teams_api.get_teams(year=2025)

for team in fbs_teams:
    if team.division == 'fbs':
        print(f"{team.school} ({team.conference})")
        print(f"  Location: {team.location}")
        print(f"  Coordinates: {team.latitude}, {team.longitude}")
```

---

## Installation and Setup

### 1. Install Python Package

```bash
pip install cfbd
```

### 2. Get API Key

1. Visit https://collegefootballdata.com
2. Create an account
3. Navigate to API Keys section
4. Generate a new API key
5. Store securely (DO NOT commit to git)

### 3. Configure Environment

**Option A: Environment Variable**
```bash
export CFBD_API_KEY="your_api_key_here"
```

**Option B: .env File** (recommended)
```
# .env (add to .gitignore!)
CFBD_API_KEY=your_api_key_here
```

**Load in Python**:
```python
import os
from dotenv import load_dotenv
import cfbd

load_dotenv()

configuration = cfbd.Configuration()
configuration.access_token = os.getenv('CFBD_API_KEY')
```

---

## Data Collection Strategy

### Initial Data Load (One-Time)

**Teams Data**:
```python
# Fetch all FBS teams for 2025
teams = teams_api.get_teams(year=2025)
fbs_teams = [t for t in teams if t.division == 'fbs']

# Filter for CFP-eligible only (implement P4/G5 filter)
cfp_teams = filter_cfp_eligible(fbs_teams)

# Save to CSV/database
save_teams(cfp_teams)
```

**Season Schedule**:
```python
# Fetch complete 2025 regular season schedule
all_games = []
for week in range(1, 16):  # Weeks 1-15
    games = games_api.get_games(
        year=2025,
        week=week,
        season_type='regular',
        division='fbs'
    )
    all_games.extend(games)

# Process and save
save_schedule(all_games)
```

**Betting Lines**:
```python
# Fetch all betting lines for 2025 season
all_lines = []
for week in range(1, 16):
    lines = betting_api.get_lines(
        year=2025,
        week=week,
        season_type='regular'
    )
    all_lines.extend(lines)

# Process and save
save_betting_lines(all_lines)
```

### Weekly Updates (During Season)

**Current Week Data**:
```python
current_week = get_current_week()

# Fetch current week games
games = games_api.get_games(
    year=2025,
    week=current_week,
    season_type='regular'
)

# Fetch current week betting lines
lines = betting_api.get_lines(
    year=2025,
    week=current_week,
    season_type='regular'
)

# Update database
update_current_week(games, lines)
```

---

## Rate Limit Management

### Free Tier Limits
- **1,000 calls/month** = ~33 calls/day
- **Strategy**: Cache aggressively, batch requests

### Optimization Tips

1. **Cache Static Data**:
   - Team information (rarely changes)
   - Historical betting lines
   - Completed game results

2. **Batch Requests**:
   - Request full week instead of individual games
   - Use filters to minimize API calls

3. **Update Schedule**:
   - Full season load: ~15 calls (15 weeks)
   - Weekly updates: 2-3 calls (games + lines)
   - Total for season: ~15 + (15 weeks × 3) = ~60 calls

4. **Development vs Production**:
   - Use cached data for development/testing
   - Only hit API for production updates

5. **Consider Patreon Tier** ($5-10/month):
   - Increased rate limits
   - GraphQL API access
   - Advanced metrics
   - Weather data

---

## Data Processing Pipeline

### Workflow

```
1. Initial Setup (One-Time)
   ├── Fetch all FBS teams → Filter CFP-eligible → Save to DB
   ├── Fetch season schedule (weeks 1-15) → Process home/away → Save to DB
   └── Fetch season betting lines → Extract spreads/totals → Save to DB

2. Weekly Updates (During Season)
   ├── Fetch current week games → Update schedules
   ├── Fetch current week lines → Update betting data
   └── Fetch previous week results → Calculate Swiss scores

3. Swiss Tournament Simulation
   ├── Load current standings
   ├── Apply home/away constraints
   ├── Generate pairings (minimum weight matching)
   └── Display matchups with betting targets
```

### Data Transformation

**From API → Our Data Model**:

```python
def process_game(api_game, api_line):
    """Transform CFBD API data to our schema"""
    return {
        'game_id': api_game.id,
        'season': api_game.season,
        'week': api_game.week,
        'home_team': api_game.home_team,
        'away_team': api_game.away_team,
        'venue': api_game.venue,
        'date': api_game.start_date,
        'home_score': api_game.home_points,
        'away_score': api_game.away_points,
        'spread': api_line.lines[0].spread if api_line.lines else None,
        'total': api_line.lines[0].over_under if api_line.lines else None,
        'home_away_status': {
            api_game.home_team: 'HOME',
            api_game.away_team: 'AWAY'
        }
    }
```

---

## Alternative Data Sources (Backup Options)

### If CFBD API Unavailable

#### For Betting Lines:
1. **The Odds API** (theoddsapi.com)
   - Commercial API, paid tiers
   - Historical odds from mid-2020
   - Aggregates multiple sportsbooks

2. **VegasInsider.com** (Web Scraping)
   - Free historical data
   - Requires web scraping (may be blocked)
   - Less reliable than API

#### For Schedules:
1. **ESPN Hidden API**
   - Endpoint: `http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard`
   - No API key required (unofficial)
   - May change without notice

2. **FBSchedules.com** (Web Scraping)
   - Clean HTML structure
   - Comprehensive coverage
   - Requires scraping, may have rate limits

3. **Sports-Reference.com** (Web Scraping)
   - Excellent historical data
   - Well-structured tables
   - May block automated access

---

## Implementation Checklist

- [ ] Install `cfbd` Python package
- [ ] Register for CFBD API key
- [ ] Set up environment variable for API key
- [ ] Add `.env` to `.gitignore`
- [ ] Create data fetching module (`src/scrapers/cfbd_client.py`)
- [ ] Implement team data fetcher
- [ ] Implement schedule data fetcher
- [ ] Implement betting lines fetcher
- [ ] Create data caching system
- [ ] Build data transformation functions
- [ ] Set up database/CSV storage
- [ ] Implement rate limit handling
- [ ] Add error handling and retries
- [ ] Create data validation tests
- [ ] Document data refresh schedule

---

## Example: Complete Data Fetcher

```python
# src/scrapers/cfbd_client.py

import os
import cfbd
from typing import List, Dict
from dotenv import load_dotenv
import pandas as pd

class CFBDClient:
    """Client for fetching data from CollegeFootballData.com API"""

    def __init__(self):
        load_dotenv()
        self.configuration = cfbd.Configuration()
        self.configuration.access_token = os.getenv('CFBD_API_KEY')

        if not self.configuration.access_token:
            raise ValueError("CFBD_API_KEY not found in environment")

    def get_teams(self, year: int = 2025) -> pd.DataFrame:
        """Fetch all FBS teams for a given year"""
        with cfbd.ApiClient(self.configuration) as api_client:
            teams_api = cfbd.TeamsApi(api_client)
            teams = teams_api.get_teams(year=year)

            # Convert to DataFrame
            teams_data = [
                {
                    'team_id': t.id,
                    'name': t.school,
                    'conference': t.conference,
                    'division': t.division,
                    'latitude': t.latitude,
                    'longitude': t.longitude,
                    'location': t.location
                }
                for t in teams if t.division == 'fbs'
            ]

            return pd.DataFrame(teams_data)

    def get_schedule(self, year: int = 2025, week: int = None) -> pd.DataFrame:
        """Fetch schedule for a given year and optional week"""
        with cfbd.ApiClient(self.configuration) as api_client:
            games_api = cfbd.GamesApi(api_client)

            if week:
                games = games_api.get_games(
                    year=year,
                    week=week,
                    season_type='regular',
                    division='fbs'
                )
            else:
                # Fetch all weeks
                games = []
                for w in range(1, 16):
                    week_games = games_api.get_games(
                        year=year,
                        week=w,
                        season_type='regular',
                        division='fbs'
                    )
                    games.extend(week_games)

            # Convert to DataFrame
            schedule_data = [
                {
                    'game_id': g.id,
                    'season': g.season,
                    'week': g.week,
                    'home_team': g.home_team,
                    'away_team': g.away_team,
                    'date': g.start_date,
                    'venue': g.venue,
                    'home_score': g.home_points,
                    'away_score': g.away_points
                }
                for g in games
            ]

            return pd.DataFrame(schedule_data)

    def get_betting_lines(self, year: int = 2025, week: int = None) -> pd.DataFrame:
        """Fetch betting lines for a given year and optional week"""
        with cfbd.ApiClient(self.configuration) as api_client:
            betting_api = cfbd.BettingApi(api_client)

            if week:
                lines = betting_api.get_lines(
                    year=year,
                    week=week,
                    season_type='regular'
                )
            else:
                # Fetch all weeks
                lines = []
                for w in range(1, 16):
                    week_lines = betting_api.get_lines(
                        year=year,
                        week=w,
                        season_type='regular'
                    )
                    lines.extend(week_lines)

            # Convert to DataFrame, taking first provider's lines
            betting_data = []
            for game in lines:
                if game.lines and len(game.lines) > 0:
                    line = game.lines[0]  # Use first provider
                    betting_data.append({
                        'game_id': game.id,
                        'season': game.season,
                        'week': game.week,
                        'home_team': game.home_team,
                        'away_team': game.away_team,
                        'spread': line.spread,
                        'total': line.over_under,
                        'provider': line.provider
                    })

            return pd.DataFrame(betting_data)


# Usage example
if __name__ == "__main__":
    client = CFBDClient()

    # Fetch teams
    teams = client.get_teams(2025)
    print(f"Fetched {len(teams)} FBS teams")

    # Fetch Week 1 schedule
    schedule = client.get_schedule(2025, week=1)
    print(f"Fetched {len(schedule)} Week 1 games")

    # Fetch Week 1 betting lines
    lines = client.get_betting_lines(2025, week=1)
    print(f"Fetched {len(lines)} betting lines")
```

---

## Summary

**Primary Data Source**: CollegeFootballData.com (CFBD) API
- **Betting Lines**: `BettingApi.get_lines()`
- **Schedules**: `GamesApi.get_games()`
- **Teams**: `TeamsApi.get_teams()`

**Key Advantages**:
- Unified API for all data needs
- Well-documented with Python wrapper
- Free tier sufficient for development
- Active maintenance and 2025 support

**Next Steps**:
1. Register for API key
2. Install cfbd package
3. Build data fetcher module
4. Implement caching system
5. Test with 2025 data

---

**Document Version**: 1.0
**Last Updated**: 2025-11-13
**API Version**: CFBD v2
**Python Package**: cfbd 4.x
