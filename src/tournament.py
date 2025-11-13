from math import sqrt
from random import random
from pathlib import Path
from typing import Optional, Set, Tuple
import logging

import networkx as nx
import pandas as pd

import utils
from schedule import TeamSchedule


class Tournament:

	def __init__(
		self,
		teams_df: pd.DataFrame,
		schedule: Optional[TeamSchedule] = None,
		use_home_away_constraint: bool = False
	):
		"""
		Initialize Swiss Tournament

		Args:
			teams_df: DataFrame of teams
			schedule: Optional TeamSchedule object for Home/Away constraints
			use_home_away_constraint: If True, only match Home teams with Away teams
		"""
		self.teams_df = teams_df
		self.schedule = schedule
		self.use_home_away_constraint = use_home_away_constraint
		self.logger = logging.getLogger(__name__)

		# Initialize tournament state
		self.round = 0
		self.teams_graph = utils.load_graph(teams_df, rebuild=True)
		# Use a copy of teams_graph to adjust distances based on W-L records
		self.adjusted_distance_graph = self.teams_graph.copy()

		# Validate schedule if using Home/Away constraint
		if self.use_home_away_constraint and self.schedule is None:
			raise ValueError(
				"Schedule must be provided when use_home_away_constraint=True"
			)

	def _apply_home_away_constraint(self, graph: nx.Graph, week: int) -> nx.Graph:
		"""
		Apply Home/Away constraint to graph (creates bipartite graph)

		Only creates edges between Home teams and Away teams.
		Removes edges between Home-Home and Away-Away pairs.

		Args:
			graph: Input graph
			week: Current week number

		Returns:
			Constrained graph (bipartite)
		"""
		if not self.use_home_away_constraint or self.schedule is None:
			return graph

		# Get teams by status
		home_teams = set(self.schedule.get_home_teams(week))
		away_teams = set(self.schedule.get_away_teams(week))
		bye_teams = set(self.schedule.get_bye_teams(week))

		self.logger.info(
			f"Week {week}: {len(home_teams)} home, {len(away_teams)} away, {len(bye_teams)} bye"
		)

		# Create constrained graph
		constrained_graph = nx.Graph()

		# Add all nodes
		for node in graph.nodes():
			constrained_graph.add_node(node)

		# Only add edges between home and away teams
		for team1, team2 in graph.edges():
			# Skip if either team is on bye
			if team1 in bye_teams or team2 in bye_teams:
				continue

			# Only add edge if one team is home and other is away
			team1_home = team1 in home_teams
			team2_home = team2 in home_teams

			if team1_home != team2_home:  # XOR: one home, one away
				weight = graph[team1][team2]['weight']
				constrained_graph.add_edge(team1, team2, weight=weight)

		self.logger.info(
			f"Constrained graph: {len(constrained_graph.nodes())} nodes, "
			f"{len(constrained_graph.edges())} edges (from {len(graph.edges())} original)"
		)

		return constrained_graph

	def get_pairings(self, verbose=False) -> set:
		"""
		Get pairings for current round using minimum weight matching

		If use_home_away_constraint is True, applies bipartite constraint
		before matching.

		Args:
			verbose: If True, saves pairings to CSV

		Returns:
			Set of tuples (team1, team2) representing pairings
		"""
		# Apply Home/Away constraint if enabled
		if self.use_home_away_constraint and self.schedule is not None:
			current_week = self.round + 1  # round starts at 0, weeks start at 1
			matching_graph = self._apply_home_away_constraint(
				self.adjusted_distance_graph,
				current_week
			)

			# Assign swiss pairings to schedule
			pairings = nx.min_weight_matching(matching_graph)
			for team1, team2 in pairings:
				self.schedule.assign_swiss_pairing(team1, team2, current_week)
		else:
			pairings = nx.min_weight_matching(self.adjusted_distance_graph)

		if verbose:
			base_path = Path(__file__).parent.parent
			output_path = base_path / "output" / f"round{ self.round }_pairings.csv"
			pair_df = pd.DataFrame(data = pairings)
			pair_df.to_csv(output_path, index=False)

		self.logger.info(f"Generated {len(pairings)} pairings for round {self.round}")

		return pairings

	def simulate_round(self):
		self.round += 1
		pairings = self.get_pairings()
		
		for team_a, team_b in pairings:    
			spread = self.teams_df.loc[team_a,'rating'] - self.teams_df.loc[team_b,'rating']
			team_a_win_prob = spread * 0.025 + 0.5
		 
			rng = random()
			winner = team_a if rng < team_a_win_prob else team_b
			loser = team_b if rng < team_a_win_prob else team_a

			self.teams_df.loc[winner,'score'] += 1
			self.teams_df.loc[winner,'wins'] += loser+' '
			self.teams_df.loc[loser,'losses'] += winner+' '
			
			self.teams_graph.remove_edge(team_a, team_b)

	def get_standings(self, verbose=False):
		standings_df = self.teams_df[["team", "score", "rating", "wins", "losses"]]
		standings_df = standings_df.sort_values(by=["score", "rating"], ascending=[False, False])
		standings_df = standings_df.drop(columns=["rating"])

		standings_df["next"] = "BYE"
		pairings = self.get_pairings()
		for team_a, team_b in pairings:
				standings_df.loc[team_a,"next"] = team_b
				standings_df.loc[team_b,"next"] = team_a

		if verbose:
			base_path = Path(__file__).parent.parent
			output_path = base_path / "output" / f"round{ self.round }_standings.csv"
			standings_df.to_csv(output_path, index=False)

		return standings_df

	def update_distances(self):
		#if team_a = team_b:
		#   break
		# if team_a.home == 'AA'
		self.adjusted_distance_graph = self.teams_graph.copy()
		for team1 in self.teams_df.index:
			for team2 in self.teams_df.index:
				if team1 == team2:
					continue
				if not self.adjusted_distance_graph.has_edge(team1, team2):
					continue
				diff = self.teams_df.loc[team1,'score'] - self.teams_df.loc[team2,'score']
				if diff > 0:
					self.adjusted_distance_graph[team1][team2]["weight"] *= (diff + 1)

	def simulate_tournament(self):

		while self.round < 12:
			self.simulate_round()
			self.update_distances()

			df = self.get_standings().to_csv(f"round{ self.round }_standings.csv")
			# self.teams_df = self.teams_df.sort_values( ['score','rating'], ascending=[False,False])
			# self.teams_df.to_csv(f"round{ self.round }_standings.csv")
			print(f"Round {self.round} complete")
			
			# choice = input(f"Start round {self.round}? (y/n): ")
			# if choice.lower() != 'y':
			#   break
