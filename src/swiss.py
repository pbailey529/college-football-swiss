from pathlib import Path

import pandas as pd

import utils
from tournament import Tournament


def start_tourney():
	teams_df = utils.load_all_teams()
	cfb = Tournament(teams_df)
	cfb.simulate_tournament()

def get_d1_teams(reload=False) -> pd.DataFrame:
	d1_conference_list = [
		"AAC",
		"ACC-ATLANTIC",
		"ACC-COASTAL",
		"BIG 12",
		"BIG TEN-EAST",
		"BIG TEN-WEST",
		"CONF-USA",
		"I-1 IND.",
		"MAC-EAST",
		"MAC-WEST",
		"MWC-MOUNTAIN",
		"MWC-WEST",
		"PAC-12 NORTH",
		"PAC-12 SOUTH",
		"SEC-EAST",
		"SEC-wEST",
		"SUN BELT EAST",
		"SUN BELT WEST",
	]
	teams_df = utils.load_all_teams(reload)
	teams_df = teams_df[teams_df['conference'].isin(d1_conference_list)]
	return teams_df

def get_p5_teams(reload=False) -> pd.DataFrame:
	d1_conference_list = [
		"ACC-ATLANTIC",
		"ACC-COASTAL",
		"BIG 12",
		"BIG TEN-EAST",
		"BIG TEN-WEST",
		"PAC-12 NORTH",
		"PAC-12 SOUTH",
		"SEC-EAST",
		"SEC-wEST",
	]
	teams_df = utils.load_all_teams(reload)
	teams_df = teams_df[teams_df['conference'].isin(d1_conference_list)]
	return teams_df
	
