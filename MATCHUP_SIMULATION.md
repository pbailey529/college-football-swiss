# Swiss Tournament Matchup Simulation System

## Overview
When two teams are matched in the Swiss tournament but playing different opponents in reality, use their actual game results to determine the Swiss tournament winner.

## Scoring Formula
```
Total Score = ATS Performance + Style Points + Win Bonus
```

### 1. ATS Performance (Base Score)
- **Calculation**: `Actual Margin - Spread`
- **Example**: If favored by 7 and win by 10, ATS = +3

### 2. Style Points (0-2 points)
Dynamic thresholds based on Vegas projected score using spread and total:
- **Projected scores**:
  - Favorite: `(Total + Spread) / 2`
  - Underdog: `(Total - Spread) / 2`
- **Offensive style point**: +1 if actual points > projected score
- **Defensive style point**: +1 if opponent scores < their projected score

**Example**: Total 50, Spread 6.5
- Favorite projected: 28.25 points (must score 29+)
- Underdog projected: 21.75 points (must hold under 22)

### 3. Win Bonus (0-N points)
- **Calculation**: Points = Number of P4 wins by your real opponent
- **Note**: Only awarded if you WIN your actual game
- **Example**: Beat Tennessee (who has 2 P4 wins) = +2 bonus

## Implementation Notes
- Display as pre-game "targets" for fan engagement
- Track "Swiss score" live during games
- Higher total score wins the Swiss tournament matchup
- For ties, use season average ATS performance as tiebreaker
