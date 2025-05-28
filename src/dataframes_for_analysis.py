import pandas as pd
from datetime import datetime
import json
from pathlib import Path
from src.functions import set_age


def load_dataframes():
    # Detect base path
    current_path = Path.cwd()
    project_name = 'world_cup_players'

    if project_name in current_path.parts:
        index = current_path.parts.index(project_name)
        project_root = Path(*current_path.parts[:index + 1])
        data_path = project_root / 'data' / 'raw' / 'json'
    else:
        raise ValueError(f"'{project_name}' not found in path")

    # Load JSONs
    df_squads = pd.read_json(fr'{data_path}/squads.json', orient='records') 
    df_player = pd.read_json(fr'{data_path}/squads.json', orient='records')
    df_player_details = pd.read_json(fr'{data_path}/df_player_details.json', orient='records')

    with open(f'{data_path}/federations.json', 'r') as f:
        federations = json.load(f)
    with open(f'{data_path}/countries.json', 'r') as f:
        countries = json.load(f)
    with open(f'{data_path}/world_cups.json', 'r') as f:
        world_cups = json.load(f)

    # Merge & transform player data
    df_player = df_player.merge(df_player_details, on='link_player', how='left').reset_index(drop=True)
    df_player['world_cup_year'] = df_player['world_cup_link'].apply(lambda x: world_cups[x]['year'])
    df_player['country'] = df_player['country_link'].map(countries)
    df_player['federation'] = df_player['country_link'].map(federations)
    df_player['club_country_link'] = df_player['club_country'].map({v: k for k, v in countries.items()})
    df_player['club_federation'] = df_player['club_country_link'].map(federations)
    df_player['born'] = df_player['born'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%d').date() if x and not isinstance(x, float) else x)
    df_player['age'] = df_player.apply(lambda x: set_age(x['born'], x['world_cup_year']), axis=1)

    # Match data
    matchs = pd.read_json(fr'{data_path}/match.json', orient='records')
    matchs_details = pd.read_json(fr'{data_path}/df_matchs_scores.json', orient='records')
    matchs['world_cup_year'] = matchs['world_cup_link'].apply(lambda x: world_cups[x]['year'])
    
 
    
    matchs['local_country'] = matchs['local_team_link'].map(countries)
    matchs['local_federation'] = matchs['local_team_link'].map(federations)
    matchs['visitor_country'] = matchs['visitor_team_link'].map(countries)
    matchs['visitor_federation'] = matchs['visitor_team_link'].map(federations)

    matchs_details = matchs_details.merge(df_player_details, left_on='player_link', right_on='link_player',  how = 'left')
    matchs_details = matchs_details.merge(matchs, left_on  = 'match', right_on  = 'match_link', how = 'left')
    matchs_details.phase = matchs_details.phase.apply(lambda x: 'Group' if 'group' in x.lower() else x)
    matchs_details = matchs_details.merge(
        df_player, on=['link_player', 'world_cup_link'], how='left', suffixes=(None, '_Duplicated'))
    to_drop = [col for col in matchs_details.columns if '_Duplicated' in col]
    matchs_details.drop(columns=to_drop, inplace=True)

    # Appearances
    appearances = pd.read_json(fr'{data_path}/appearances.json', orient='records')
    appearances['world_cup_year'] = appearances['world_cup_link'].apply(lambda x: world_cups[x]['year'])
    appearances['country'] = appearances['country_link'].map(countries)
    appearances['appearances'] = appearances['appearances'].apply(lambda x: int(x) if x != '-' else 0)

    return df_player, matchs, matchs_details, appearances
