from math import sqrt
from random import random
from pathlib import Path

import networkx as nx
import pandas as pd

import utils


class Tournament:

	def __init__(self, teams_df: pd.DataFrame):
		self.teams_df = teams_df
		# self.teams_df.drop(columns=['lat', 'long'])
		# self.teams_df["wins"] = ''
		# self.teams_df["losses"] = ''
		# # Initialize empty lists for wins and losses
		# self.teams_df['W'] = [[] for _ in range(len(self.teams_df))]
		# self.teams_df['L'] = [[] for _ in range(len(self.teams_df))]
		self.round = 0
		self.teams_graph = utils.load_graph(teams_df, rebuild=True)
		# Use a copy of teams_graph to adjust distances based on W-L records
		self.adjusted_distance_graph = self.teams_graph.copy()

	def get_pairings(self, verbose=False) -> set:
		pairings = nx.min_weight_matching(self.adjusted_distance_graph)

		if verbose:
			base_path = Path(__file__).parent.parent
			output_path = base_path / "output" / f"round{ self.round }_pairings.csv"
			pair_df = pd.DataFrame(data = pairings)
			pair_df.to_csv(output_path, index=False)

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
