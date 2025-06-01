#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 18:15:19 2024

@author: sebastian
"""


# libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import re
import os 
import json
from pathlib import Path








## FUNCTIONS
def extract_numbers(string):
    pattern = r'(\d+)\((\d+)\+(\d+)\)' # Corrected regex: use \+ for the plus sign
    match = re.match(pattern, string)
    if match:
        outside_parenthesis = int(match.group(1))
        inside_parenthesis_first = int(match.group(2))
        inside_parenthesis_second = int(match.group(3))
        return [outside_parenthesis, inside_parenthesis_first, inside_parenthesis_second]
    else:
        return [None, None, None] # Return a list of None values, not just None





current_path = Path.cwd()
project_name = 'world_cup_players'
# Look for the project folder in the path
if project_name in current_path.parts:
    index = current_path.parts.index(project_name)
    project_root = Path(*current_path.parts[:index + 1])
    data_path = project_root / 'data' / 'raw' / 'json'
    functions_path = project_root / 'src'

else:
    raise ValueError(f"'{project_name}' not found in path")



with open(f'{data_path}/world_cups.json', 'r') as f:
    world_cups  = json.load(f)
    

player_scores = []
for world_cup_link, world_cup  in world_cups.items():
    print(world_cup_link)
    try:
        # the format of the url for the semifinal of a cup
        # example url = f'https://www.worldfootball.net/schedule/wm-2022-in-katar-halbfinale/0/'
        url = f'https://www.worldfootball.net/scorer{world_cup_link}'
        response = requests.get(url)
        api = requests.get(url)
        soup = BeautifulSoup(api.text, 'lxml')
        # table with personal details
        table = soup.find('table', class_='standard_tabelle').find_all('tr')
        
        for row in table:
            cols = row.find_all(['td'])
            cols = [col.get_text(strip=True) for col in cols] # to comment
            #We get the api of the player to get more information further. 
            # It will be used as id as well because of existence of duplication with names).
            links = row.find_all('a')
            href_link = links[0]['href'] if links else None
            row_data = cols + [href_link] + [world_cup_link] 
            player_scores.append(row_data)
    except Exception as error:
        print(error)
        
        
df_player_scores = pd.DataFrame(player_scores)
# we drop columns not desired from row.find_all(['td'])
df_player_scores.drop(columns= [2], axis=1, inplace=True) 
df_player_scores.columns=['ranking_score', 'name', 'country', 'team', 'goals_string','link_player', 'world_cup_link' ]
#  we remove rows without player information
df_player_scores = df_player_scores.dropna(subset = ['link_player'])
df_player_scores.reset_index(drop = True, inplace = True)
df_player_scores.to_json(path_or_buf = f'{data_path}/df_player_scores.json',orient='records')


for index, row in df_player_scores.iterrows():
    if row['ranking_score'] =='':
        df_player_scores.iloc[index,0] = df_player_scores.iloc[index- 1,0] 

# df_player_scores.ranking_score = df_player_scores.ranking_score.apply(lambda x: int(x.replace('.','')))
df_player_scores['goals'], df_player_scores['field_goals'], df_player_scores['penalty_goals'], = zip(*df_player_scores['goals_string'].apply(lambda x: extract_numbers(x)))

player_assists = []
for world_cup_link,world_cup  in world_cups.items():
    print(world_cup_link)
    try:
        # the format of the url for the semifinal of a cup
        # example url = f'https://www.worldfootball.net/schedule/wm-2022-in-katar-halbfinale/0/'
        url = f'https://www.worldfootball.net/assists{world_cup_link}'
        response = requests.get(url)
        api = requests.get(url)
        soup = BeautifulSoup(api.text, 'lxml')
        # table with personal details
        table = soup.find('table', class_='standard_tabelle').find_all('tr')
        
        for row in table:
            cols = row.find_all(['td'])
            cols = [col.get_text(strip=True) for col in cols] # to comment
            #We get the api of the player to get more information further. 
            # It will be used as id as well because of existence of duplication with names).
            links = row.find_all('a')
            href_link = links[0]['href'] if links else None
            row_data = cols + [href_link] + [world_cup_link] 
            player_assists.append(row_data)
    except Exception as error:
        print(error)
        
        
df_player_assists = pd.DataFrame(player_assists)
# we drop columns not desired from row.find_all(['td'])
df_player_assists.drop(columns= [2], axis=1, inplace=True) 
df_player_assists.columns=['ranking_score', 'name', 'country', 'team', 'assists','link_player', 'world_cup_link' ]
#  we remove rows without player information
df_player_assists = df_player_assists.dropna(subset = ['link_player'])
df_player_assists.reset_index(drop = True, inplace = True)

for index, row in df_player_assists.iterrows():
    if row['ranking_score'] =='':
        df_player_assists.iloc[index,0] = df_player_assists.iloc[index- 1,0] 

df_player_assists.assists = df_player_assists.assists.astype(int)
df_player_assists.ranking_score = df_player_assists.ranking_score.apply(lambda x: int(x.replace('.','')))

df_player_assists.to_json(path_or_buf = f'{data_path}/df_player_assists.json',orient='records')
