from pathlib import Path

import pandas as pd

import utils
from tournament import Tournament


def start_tourney():
	teams_df = utils.load_all_teams()
	cfb = Tournament(teams_df)
	cfb.simulate_tournament()

def get_d1_teams(reload=False) -> pd.DataFrame:
	"""
	Legacy function: Get all FBS teams (D1)
	NOTE: Conference structure reflects pre-2024 realignment
	For 2025 season, use get_cfp_eligible_teams() instead
	"""
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
	"""
	Legacy function: Get Power 5 teams (pre-2024 realignment)
	NOTE: For 2025 season, use get_p4_teams() instead (Power 4)
	"""
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

def get_p4_teams(reload=False) -> pd.DataFrame:
	"""
	Get Power 4 teams for 2025 season (post-realignment)
	Includes: Big Ten, SEC, ACC, Big 12
	Note: Pac-12 dissolved; teams moved to P4 conferences
	"""
	p4_conferences = [
		"BIG TEN",
		"SEC",
		"ACC",
		"BIG 12",
	]
	teams_df = utils.load_all_teams(reload)
	teams_df = teams_df[teams_df['conference'].isin(p4_conferences)]
	return teams_df

def get_g5_teams(reload=False) -> pd.DataFrame:
	"""
	Get Group of 5 teams for 2025 season
	Includes: American (AAC), Conference USA, MAC, Mountain West, Sun Belt
	"""
	g5_conferences = [
		"AAC",           # American Athletic Conference
		"CONF-USA",      # Conference USA
		"MAC",           # Mid-American Conference
		"MWC",           # Mountain West Conference
		"SUN BELT",      # Sun Belt Conference
	]
	teams_df = utils.load_all_teams(reload)
	teams_df = teams_df[teams_df['conference'].isin(g5_conferences)]
	return teams_df

def get_cfp_eligible_teams(reload=False) -> pd.DataFrame:
	"""
	Get all CFP-eligible teams for 2025 season
	Includes: P4 conferences + Notre Dame + G5 conferences
	Excludes: FCS, Division II, Division III

	Returns:
		pd.DataFrame: All teams eligible for College Football Playoff
	"""
	cfp_conferences = [
		# Power 4
		"BIG TEN",
		"SEC",
		"ACC",
		"BIG 12",
		# Group of 5
		"AAC",
		"CONF-USA",
		"MAC",
		"MWC",
		"SUN BELT",
		# Independents (CFP-eligible only)
		"FBS IND",       # Notre Dame
	]

	teams_df = utils.load_all_teams(reload)

	# Filter by conference
	cfp_teams = teams_df[teams_df['conference'].isin(cfp_conferences)]

	# Ensure Notre Dame is included (special case as independent)
	# If conference data uses different naming, check by team name too
	notre_dame_check = teams_df[teams_df['team'].str.contains('Notre Dame', case=False, na=False)]
	if not notre_dame_check.empty and notre_dame_check.index[0] not in cfp_teams.index:
		cfp_teams = pd.concat([cfp_teams, notre_dame_check])

	return cfp_teams
	
