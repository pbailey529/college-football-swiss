# College Football Swiss
Imagine a college football season where every game matters,  without the headaches and heartbreaks of conference realignment. Welcome to the College Football Swiss Tournament! **Every week, teams play the closest geographical opponent with a similar win-loss record**. Win, and you'll climb the rankings, facing tougher challengers. Lose, and you'll battle to redeem yourself against teams with a similar setback. It’s a thrilling, high-stakes journey that gives every team something to play for till the final whistle. At the same time, we're renewing regional rivalries, and creating new ones that should have existed all along!

### What is a Swiss Tournament?
A [Swiss tournament](https://en.wikipedia.org/wiki/Swiss-system_tournament) is a format often used in chess and other sports, where each competitor plays a fixed number of matches against opponents with a similar number of wins and losses. The key advantages are:

* Efficiency: The most elite teams will be identified in far fewer rounds than a round-robin format. For example, a tournament with over 1000 players can determine a champion in as few as 10 rounds.
* Fairness: Teams are matched against others with a similar win/loss record. Teams are never eliminated from the tournament.
* Excitement: Each game is crucial, because matchups will change dynamically based on previous results, keeping the stakes high throughout the entire season.

### How are you doing this for college football?
We represent the college football landscape as a Network Graph, where Nodes are the college football teams, and Edges represent the geographic distance between each team. We use the [Minimum Weight Matching](https://en.wikipedia.org/wiki/Matching_(graph_theory)#Maximum-weight_matching) algorithm from graph theory to pair teams such that the total travel distance is minimized. After each round, we update the network in two steps. First, we increase edge weights between teams with differing records to reduce future pairings of unevenly matched teams. Then, we remove edges between teams that have already played. The Swiss format maintains competitive balance throughout the tournament, providing a dynamic, fair, and logistically optimized tournament structure.

# Installaton and setup
Clone the repo, then run the following commands:
```bsh
cd college-football-swiss
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
jupyter notebook notebooks/swiss.ipynb
```

# Known Issues and Next Steps
1. Tweak the distance adjustment to make very nearby teams with dissimilar records not overcome the distance adjustment.
    * Currently, in larger tournaments, an undefeated 6-win team can be paired with a 4-win team nearby, since other undefeated 6-win teams are too far away.
    * I'm envisioning teams initially plotted on a 2d plane in 3 dimensions, and each point different from a .500 record changes their "elevtion" from that plane, and each elevation level also brings teams closer together. At the end of a season, teams will be shaped like a diamond pyramid. 3d distances are then calculated
    * Perhaps teams are plotted on the surface of a globe, and brought closer to the center/origin of the sphere when their record changes.
1. Create Home and Away schedules
    * Perhaps dynamically create home and away schedules such that no team ever plays 3 home or away games in a row (eg, remove the edge between two teams if their last two games were both at home)
    * Alternatively, pre-set the home and away schedules at the beginning of the season, and only pair teams with a homegame each week with teams with an away game that week
1. Tweak the algorithm so that matchups are generated two weeks in advance, to allow for more realistic scheduling, overcoming logistical challenges.
    * In theory, teams and fans would need advance notice in order to arrange travel accommodations, etc.
    * Make this a setting when initializing the tournament, to set the number of weeks ahead each matchup will be predicted.
    * In theory, teams would schedule marquee matchups or cupcakes in weeks 1 and 2, and then their records would determine their next opponents as usual.
1. Simulate past seasons by going back and gathering the performance vs the spread from each week, and using that to generate records. 
    * Eg. GT vs UCF week 4, in 2006, GT was +5 against the spread and UCF was +14. So in our simulated tournament, UCF beats GT in week 4.