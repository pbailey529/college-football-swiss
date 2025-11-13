# College Football Swiss Tournament - Feature Documentation

## Project Management

### Task Management Tool
**Use `bd` (beads) for all task management**
- Beads has been installed and initialized in this repository
- Database location: `.beads/beads.db`
- Issue prefix: `college-football-swiss`
- Git hooks and merge driver configured
- Always use `export PATH="$PATH:/root/go/bin"` before running `bd` commands

### Beads Usage
```bash
export PATH="$PATH:/root/go/bin"
bd new "Task description"           # Create a new task
bd list                             # List all tasks
bd show <issue-id>                  # Show task details
bd edit <issue-id>                  # Edit a task
bd done <issue-id>                  # Mark task as done
bd quickstart                       # Get started guide
```

---

## Project Overview

This project implements a Swiss-system tournament for college football, where teams are paired each week based on their win-loss records while minimizing travel distance. Unlike traditional conference play, this creates a dynamic, fair, and exciting format where every game matters.

### Core Concept
- **Geographic Matching**: Teams play the closest geographical opponent with a similar win-loss record
- **Swiss Tournament**: No eliminations, continuous meaningful competition
- **Dynamic Pairings**: Matchups change week-by-week based on results
- **Home/Away Balance**: Constraints ensure realistic travel patterns

---

## Team Eligibility Scope

### Current Scope: CFP-Eligible Teams Only
The system is currently limited to teams eligible for the College Football Playoff (CFP):

#### P4 Conferences (Power 4)
1. **Big Ten** (18 teams as of 2024)
2. **SEC** (16 teams as of 2024)
3. **ACC** (17 teams including Notre Dame scheduling agreement)
4. **Big 12** (16 teams as of 2024)

#### Independent
- **Notre Dame** (CFP-eligible independent)

#### G5 Conferences (Group of 5)
1. **American Athletic Conference (AAC)**
2. **Conference USA (C-USA)**
3. **Mid-American Conference (MAC)**
4. **Mountain West Conference (MWC)**
5. **Sun Belt Conference**

**Total**: Approximately 130-135 FBS teams eligible for CFP consideration

### Future Expansion Plans
- **Phase 2**: Include all FCS teams (Football Championship Subdivision)
- **Phase 3**: Potentially expand to Division II and Division III
- Note: Expansion plans are documented but not yet implemented

---

## Matchup Simulation System

### Overview
When two teams are matched in the Swiss tournament but are playing different opponents in reality (which is the norm), we use their actual game results to determine the Swiss tournament winner.

### Detailed Scoring System

#### Formula
```
Total Swiss Score = ATS Performance + Style Points + Win Bonus
```

#### 1. ATS Performance (Base Score)
**Against The Spread performance**
- Calculation: `Actual Margin - Spread`
- Example: Team favored by 7, wins by 10 → ATS = +3
- Example: Team underdog by 3, loses by 1 → ATS = +2
- This is the foundational metric for Swiss tournament scoring

#### 2. Style Points (0-2 points)
**Reward dominant offensive and defensive performance**

Dynamic thresholds based on Vegas projected scores:
- **Projected Scores Calculation**:
  - Favorite: `(Total + Spread) / 2`
  - Underdog: `(Total - Spread) / 2`

- **Offensive Style Point**: +1 if actual points > projected score
- **Defensive Style Point**: +1 if opponent scores < their projected score

**Example**:
- Vegas Total: 50, Spread: 6.5
- Favorite projected score: (50 + 6.5) / 2 = 28.25 points
  - Must score 29+ for offensive style point
  - Must hold opponent under 22 for defensive style point
- Underdog projected score: (50 - 6.5) / 2 = 21.75 points
  - Must score 22+ for offensive style point
  - Must hold opponent under 29 for defensive style point

#### 3. Win Bonus (0-N points)
**Strength of victory metric**
- Points = Number of P4 conference wins by your real opponent
- Only awarded if you WIN your actual game
- Example: Beat Tennessee (who has 2 P4 wins) = +2 bonus points
- Rewards teams for beating quality opponents
- Does not apply if you lose

### Swiss Tournament Winner Determination
- Team with higher Total Swiss Score wins the Swiss matchup
- **Tiebreaker**: Season average ATS performance
- Both teams' scores are recorded for tournament standings

### Implementation Features
- Display pre-game "targets" for fan engagement
- Track "Swiss score" live during games
- Maintain running statistics for tiebreaker calculations

**Reference**: See `MATCHUP_SIMULATION.md` for complete scoring system details

---

## Data Sources and Scraping

### Vegas Betting Lines (2025 Season)
**Required Data**:
- Point spreads for all FBS games
- Over/Under totals for all FBS games
- Updated weekly throughout the season

**Potential Sources** (to be evaluated):
1. **OddsShark** - Historical and current lines
2. **Covers.com** - Comprehensive coverage
3. **TheLines.com** - Multiple sportsbooks aggregated
4. **Action Network** - Professional betting data
5. **ESPN Bet** - Integrated with ESPN schedule data
6. **VegasInsider** - Long-standing odds provider

**Selection Criteria**:
- Reliability and completeness of historical data
- Ease of scraping (structure, rate limits, etc.)
- Consistency of data format
- Single sportsbook sufficient (no need to aggregate "best odds")

**Data to Collect**:
```python
{
    "game_id": str,
    "date": datetime,
    "team_a": str,
    "team_b": str,
    "spread": float,        # Negative for favorite
    "total": float,         # Over/Under
    "sportsbook": str       # For reference
}
```

### Team Schedules (2025 Season)
**Required Data**:
- Complete schedule for each team
- Home/Away designation for each game
- Bye weeks
- Week numbers (1-15 for regular season)

**Potential Sources** (to be evaluated):
1. **fbschedules.com**
   - Pros: Dedicated to CFB schedules, clean format
   - Cons: May need to scrape individual team pages

2. **sports-reference.com/cfb**
   - Pros: Comprehensive data, well-structured
   - Cons: May have rate limiting

3. **CBSSports.com**
   - Pros: Official data, reliable
   - Cons: More complex page structure

4. **ESPN.com**
   - Pros: Official, comprehensive
   - Cons: Dynamic loading, may require API access

**Selection Criteria**:
- Complete coverage of all CFP-eligible teams
- Clear Home/Away designation
- Reliable and consistent data structure
- Minimal rate limiting or access restrictions

**Data to Collect**:
```python
{
    "team": str,
    "week": int,
    "opponent": str,
    "home_away_bye": str,  # 'HOME', 'AWAY', or 'BYE'
    "date": datetime,
    "location": str         # Stadium name/city (optional)
}
```

---

## Swiss Tournament Constraints

### Home/Away Matching Rule
**Core Constraint**: Teams playing an Away game can ONLY be matched against teams playing a Home game.

**Rationale**:
- Simulates real-world travel logistics
- Maintains competitive balance
- Creates realistic scheduling scenarios
- Prevents scenarios where teams would need to "travel" to play each other when both are away

**Implementation**:
1. Filter teams by game status each week:
   - Home teams pool
   - Away teams pool
   - Bye teams (excluded from matchups)

2. When generating pairings:
   - Only create edges between Home and Away teams
   - Remove edges between Home-Home and Away-Away teams
   - Apply Swiss system matching within this constrained graph

3. Graph theory approach:
   - Bipartite graph structure
   - Home teams as one partition
   - Away teams as second partition
   - Minimum weight matching on bipartite graph

**Edge Cases**:
- Unequal numbers of Home vs Away teams in a given week
- Handling Bye weeks (teams on bye don't participate)
- Week 1 special case (if needed for pre-set schedules)

---

## Data Models

### Team Data
```python
{
    "team_id": str,              # Unique identifier
    "name": str,                 # Team name
    "conference": str,           # Conference affiliation
    "division": str,             # P4, G5, IND
    "latitude": float,           # Geographic location
    "longitude": float,          # Geographic location
    "rating": float,             # Team strength rating (e.g., ELO, SP+)
    "cfp_eligible": bool         # CFP eligibility flag
}
```

### Schedule Data
```python
{
    "team_id": str,
    "season": int,               # e.g., 2025
    "week": int,                 # 1-15 (regular season)
    "real_opponent": str,        # Actual scheduled opponent
    "home_away_bye": str,        # 'HOME', 'AWAY', 'BYE'
    "venue": str,                # Stadium name
    "city": str,                 # City, State
    "swiss_opponent": str,       # Assigned Swiss tournament opponent
    "swiss_pairing_id": str      # Links two teams in Swiss pairing
}
```

### Game Results Data
```python
{
    "game_id": str,
    "season": int,
    "week": int,
    "team_a": str,
    "team_b": str,
    "team_a_score": int,
    "team_b_score": int,
    "spread": float,             # Vegas line
    "total": float,              # Vegas O/U
    "team_a_ats": float,         # ATS performance
    "team_b_ats": float,
    "team_a_style_offense": int, # 0 or 1
    "team_a_style_defense": int, # 0 or 1
    "team_b_style_offense": int,
    "team_b_style_defense": int,
    "team_a_win_bonus": int,     # Opponent's P4 wins
    "team_b_win_bonus": int
}
```

### Swiss Tournament State
```python
{
    "season": int,
    "current_week": int,
    "teams": [
        {
            "team_id": str,
            "wins": int,
            "losses": int,
            "swiss_points": float,      # Cumulative Swiss score
            "avg_ats": float,           # Season average ATS
            "opponents_played": [str],  # List of team_ids
            "home_away_record": {
                "home_games": int,
                "away_games": int,
                "byes": int
            }
        }
    ],
    "pairings_history": [
        {
            "week": int,
            "team_a": str,
            "team_b": str,
            "team_a_swiss_score": float,
            "team_b_swiss_score": float,
            "winner": str
        }
    ]
}
```

---

## Technical Architecture

### Current Implementation
- **Language**: Python 3.x
- **Graph Library**: NetworkX
- **Data Processing**: Pandas
- **Algorithms**: Minimum Weight Matching
- **Visualization**: Jupyter Notebooks

### Core Components

#### 1. Tournament Class (`src/tournament.py`)
- Swiss tournament logic
- Pairing generation
- Distance-based matching
- Record-based edge weight adjustment

#### 2. Team Management (`src/swiss.py`)
- Team loading and filtering
- Conference-based filtering
- Historical P5/P4 filtering
- Future: CFP-eligible filtering

#### 3. Utilities (`src/utils.py`)
- Graph construction
- Distance calculations
- Data loading helpers

### Planned Enhancements

#### Web Scraping Module
```
src/
├── scrapers/
│   ├── __init__.py
│   ├── odds_scraper.py      # Vegas lines
│   ├── schedule_scraper.py  # Team schedules
│   └── results_scraper.py   # Game results
```

#### Data Storage
```
data/
├── raw/
│   ├── teams.csv
│   ├── schedules_2025.csv
│   ├── odds_2025.csv
│   └── results_2025.csv
├── processed/
│   └── swiss_state.json
└── cache/
    └── <scraped_data_cache>
```

#### Swiss Scoring Module
```
src/
├── scoring/
│   ├── __init__.py
│   ├── ats_calculator.py
│   ├── style_points.py
│   ├── win_bonus.py
│   └── swiss_scorer.py
```

---

## Algorithm Details

### Geographic Matching with Record Constraints

#### Graph Construction
1. **Nodes**: All CFP-eligible teams
2. **Edges**: Connections between teams that could play
3. **Edge Weights**: Distance adjusted by record difference

#### Weight Calculation
```python
base_weight = geographic_distance(team_a, team_b)
record_penalty = abs(team_a.wins - team_b.wins) + 1
adjusted_weight = base_weight * record_penalty
```

#### Home/Away Constraint (NEW)
```python
# Only create edges between Home and Away teams
if (team_a.status == 'HOME' and team_b.status == 'AWAY') or \
   (team_a.status == 'AWAY' and team_b.status == 'HOME'):
    graph.add_edge(team_a, team_b, weight=adjusted_weight)
```

#### Matching Algorithm
```python
pairings = nx.min_weight_matching(adjusted_graph)
```

### Distance Adjustment Evolution
Current approach uses linear record difference multiplication. Future considerations:
- **3D Elevation Model**: Teams plotted on 2D plane with elevation based on record
- **Spherical Model**: Teams on globe surface, pulled toward center based on record difference
- **Goal**: Prevent nearby teams with very different records from being paired

---

## Workflow and Process

### Season Initialization
1. Load CFP-eligible teams
2. Scrape complete season schedules
3. Scrape Vegas lines for all games
4. Initialize Swiss tournament state
5. Set week 1 pairings (or allow pre-scheduled games)

### Weekly Process
1. **Pre-Game**:
   - Display Swiss tournament pairings
   - Show scoring targets for each team
   - Calculate projected scores from Vegas lines

2. **During Games**:
   - Track real game results
   - Calculate running Swiss scores
   - Update live standings

3. **Post-Game**:
   - Calculate final Swiss scores
   - Determine Swiss matchup winners
   - Update tournament standings
   - Adjust graph weights based on new records
   - Remove edges between teams that played
   - Apply Home/Away constraints for next week
   - Generate next week's pairings

### Data Pipeline
```
1. Scrape Vegas Lines → 2. Scrape Schedules → 3. Load Teams
         ↓
4. Initialize Tournament State
         ↓
5. Generate Week N Pairings (with Home/Away constraint)
         ↓
6. Real Games Played → 7. Scrape Results
         ↓
8. Calculate Swiss Scores → 9. Update Standings
         ↓
10. Update Graph → 11. Generate Week N+1 Pairings
         ↓
Repeat steps 6-11
```

---

## Implementation Roadmap

### Phase 1: Data Infrastructure (Current)
- [x] Install and configure `bd` (beads) tool
- [ ] Research and select Vegas lines data source
- [ ] Research and select schedule data source
- [ ] Build web scraping modules
- [ ] Define and implement data models
- [ ] Set up data storage structure

### Phase 2: CFP Team Filtering
- [ ] Update team loading to filter CFP-eligible only
- [ ] Add P4 conference definitions (2024-2025 realignment)
- [ ] Add G5 conference definitions
- [ ] Include Notre Dame as independent
- [ ] Remove FCS and lower divisions

### Phase 3: Home/Away Constraints
- [ ] Add home/away status to team data
- [ ] Implement bipartite graph constraint
- [ ] Modify matching algorithm for Home/Away rule
- [ ] Handle edge cases (unequal numbers, byes)
- [ ] Test constraint enforcement

### Phase 4: Swiss Scoring System
- [ ] Implement ATS calculation
- [ ] Implement Style Points calculator
- [ ] Implement Win Bonus system
- [ ] Build Swiss score aggregator
- [ ] Add tiebreaker logic
- [ ] Create scoring display/reporting

### Phase 5: Integration and Testing
- [ ] Integrate all components
- [ ] Test with historical data
- [ ] Validate scoring accuracy
- [ ] Verify constraint enforcement
- [ ] Performance optimization

### Phase 6: Visualization and Reporting
- [ ] Update Jupyter notebooks
- [ ] Create standings displays
- [ ] Build matchup preview displays
- [ ] Generate weekly reports
- [ ] Create season summary analytics

### Phase 7: Future Enhancements
- [ ] Two-week advance scheduling option
- [ ] Historical season simulation
- [ ] FCS expansion
- [ ] Advanced distance adjustment models
- [ ] Interactive web interface

---

## Testing Strategy

### Unit Tests
- ATS calculation accuracy
- Style Points calculation
- Win Bonus assignment
- Home/Away constraint enforcement
- Graph weight calculations

### Integration Tests
- Full week simulation
- Multi-week tournament progression
- Data scraping reliability
- Edge case handling

### Validation Tests
- Historical data verification
- Scoring system validation
- Constraint verification
- Performance benchmarks

---

## Known Issues and Considerations

### Current Known Issues
1. **Distance Adjustment**: Very nearby teams with dissimilar records can still be paired
   - Proposed solution: 3D elevation or spherical model

2. **Home/Away Balance**: Need to ensure no team plays 3+ consecutive home or away games
   - Current solution: Pre-set schedules with constraint enforcement

### Design Decisions
1. **Single Sportsbook**: Using one sportsbook's lines is sufficient; no need to aggregate
2. **CFP-Only Scope**: Limiting to CFP-eligible teams for initial implementation
3. **Home/Away Constraint**: Strict enforcement for realistic simulation
4. **Swiss Scoring**: Using actual game results, not hypothetical head-to-head

### Future Considerations
1. **Advance Scheduling**: Option for 2-week advance pairings for logistics
2. **Week 1-2 Handling**: Allow pre-scheduled marquee matchups or cupcakes
3. **Bye Week Distribution**: Ensure fair bye week distribution
4. **Rating System**: Choose team rating system (ELO, SP+, FPI, etc.)

---

## References

### External Documentation
- [Swiss Tournament System - Wikipedia](https://en.wikipedia.org/wiki/Swiss-system_tournament)
- [Minimum Weight Matching - Wikipedia](https://en.wikipedia.org/wiki/Matching_(graph_theory)#Maximum-weight_matching)
- [NetworkX Documentation](https://networkx.org/documentation/stable/)

### Related Files
- `README.md` - Project overview and setup
- `MATCHUP_SIMULATION.md` - Detailed scoring system
- `src/tournament.py` - Core tournament logic
- `src/swiss.py` - Team management
- `notebooks/swiss.ipynb` - Interactive simulation

---

## Contributing

### For New Features
1. Create task in `bd`: `bd new "Feature description"`
2. Create feature branch: `git checkout -b feature/description`
3. Implement with unit tests
4. Update this documentation
5. Submit pull request
6. Mark task complete: `bd done <issue-id>`

### For Bug Fixes
1. Create task in `bd`: `bd new "Bug: description"`
2. Create bugfix branch: `git checkout -b bugfix/description`
3. Fix with regression test
4. Update documentation if needed
5. Submit pull request
6. Mark task complete: `bd done <issue-id>`

---

## Appendix

### Conference Realignment (2024-2025)

#### Big Ten (18 teams)
- Added: USC, UCLA, Oregon, Washington

#### SEC (16 teams)
- Added: Texas, Oklahoma

#### ACC (17 teams)
- Added: Stanford, California, SMU

#### Big 12 (16 teams)
- Added: UCF, Cincinnati, Houston, BYU, Arizona, Arizona State, Colorado, Utah
- Lost: Texas, Oklahoma to SEC

#### Pac-12 (Dissolved)
- Remaining: Oregon State, Washington State (rebuilding)

### Team Rating Systems (Options)
- **ELO Rating**: Chess-style rating system
- **SP+ (ESPN)**: Success rate and explosiveness
- **FPI (ESPN)**: Football Power Index
- **Sagarin Ratings**: Computer ranking
- **Massey Ratings**: Mathematical ranking
- **AP/Coaches Poll**: Human rankings (less objective)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-13
**Maintained By**: Claude (AI Assistant)
**Repository**: college-football-swiss
