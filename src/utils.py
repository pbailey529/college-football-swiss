import os
import pickle
from pathlib import Path

import pandas as pd
import networkx as nx
from geopy.distance import geodesic


def load_all_teams(reload=False) -> pd.DataFrame:
	base_path = Path(__file__).parent.parent
	pickle_path = base_path / 'pickle' / 'cfb_teams_df.pickle'
	teams_path = base_path / 'input' / 'cfb_teams.csv'

	if reload == False and os.path.exists(pickle_path):
		with open(pickle_path, 'rb') as handle:
			teams_df = pickle.load(handle)
	else:
		teams_df = pd.read_csv(teams_path, index_col="nickname")
		# teams_df['wins'] = teams_df['wins'].astype(str)
		# teams_df['losses'] = teams_df['losses'].astype(str)
		teams_df['wins'] = ''
		teams_df['losses'] = ''
		# for team in teams_df.index:
		#   teams_df.loc[team,'wins'] = ''
		#   teams_df.loc[team,'losses'] = ''
		teams_df = teams_df.drop(columns=['lat', 'long'])
		with open(pickle_path, 'wb') as handle:
			pickle.dump(teams_df, handle)
	return teams_df

def build_graph(teams_df: pd.DataFrame) -> nx.Graph:
	teams_graph = nx.Graph() 

	for nickname1 in teams_df.index:
		teams_graph.add_node(nickname1)
		for nickname2 in teams_df.index:
			if nickname1 == nickname2:
				break
			coord1 = eval(teams_df.loc[nickname1, 'coords'])
			coord2 = eval(teams_df.loc[nickname2, 'coords'])
			distance = geodesic(coord1, coord2).miles
			teams_graph.add_edge(nickname1, nickname2, weight=distance)
	return teams_graph

def load_graph(teams_df: pd.DataFrame, rebuild=False) -> nx.Graph:
	base_path = Path(__file__).parent.parent
	pickle_path = base_path / 'pickle' / 'cfb_distance_graph.pickle'
	
	if rebuild == False and os.path.exists(pickle_path):
		with open(pickle_path, 'rb') as handle:
			teams_graph = pickle.load(handle)
	else:
		teams_graph = build_graph(teams_df)    
		
		with open(pickle_path, 'wb') as handle:
			pickle.dump(teams_graph, handle)
	return teams_graph

# # TODO: Fix RPI calculation
# def calculate_wp(df):  
# 	# Calculate WP
# 	df['G'] = df['wins'].apply(len) + df['losses'].apply(len)
# 	df['WP'] = df['wins'].apply(len) / df['G'] if df['G'] > 0 else 0

# # df['OWP'] = df.apply(lambda row: calculate_owp(row, df), axis=1)
# def calculate_owp(row, df):
# 	opponents = row['wins'] + row['losses']
# 	if opponents:
# 		opponent_wps = [df[df['team_name'] == opponent]['WP'].values[0] for opponent in opponents if df[df['team_name'] == opponent]['WP'].values.size > 0]
# 		return sum(opponent_wps) / len(opponent_wps)
# 	return 0

# # df['OOWP'] = df.apply(lambda row: calculate_oowp(row, df), axis=1)
# def calculate_oowp(row, df):
# 	opponents = row['wins'] + row['losses']
# 	opponent_owps = [df[df['team_name'] == opponent]['OWP'].values[0] for opponent in opponents if df[df['team_name'] == opponent]['OWP'].values.size > 0]
# 	if opponent_owps:
# 		return sum(opponent_owps) / len(opponent_owps)
# 	return 0



# def extract_csv_from_xlsx():
#   xlsx = pd.ExcelFile('input/CFB.xlsx')
#   df = pd.read_excel(xlsx, 'cfb_teams') 
#   df.to_csv('input/cfb_teams.csv', index=False)