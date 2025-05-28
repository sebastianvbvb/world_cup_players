#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 08:36:39 2023

@author: sebastian
"""

# 




# libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import json
import os
from pathlib import Path
    
    

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
    
    

with open(f'{data_path}/countries.json', 'r') as f:
    countries  = json.load(f)
    
with open(f'{data_path}/world_cups.json', 'r') as f:
    world_cups  = json.load(f)
    
    
# squads contain combination of country and cup only if exists
squads = pd.read_json(f'{data_path}/squads.json',orient='records') 
country_appearances = squads[['world_cup_link', 'country_link']].drop_duplicates()
# converting  dataframe to list it make possible iter over it
country_appearances = [list(row) for index, row in country_appearances.iterrows()]



player_list = []
errors = []
def fetch_data(world_cup_link, country_link  ):
    try:
        # the format of the url that have a table with some measures during the cup for every player
        #  example https://www.worldfootball.net/team_performance//teams/deutschland-team/-team//wm-2022-in-katar/
        url = f"https://www.worldfootball.net/team_performance/{country_link}-team/{world_cup_link}"
        api = requests.get(url)
        soup = BeautifulSoup(api.text, 'lxml')
        table = soup.find('table', class_='standard_tabelle').find_all('tr')
        data = []
        for row in table:
            # information appear in td tags
            cols = row.find_all(['td'])
            cols = [col.get_text(strip=True) for col in cols]
            if cols[0] != 'Name': # name is how starts the first row with headers of the table
                  # we look for the player link to join by 
                  links = row.find_all('a')
                  player_link = links[0]['href'] if links else None
                  your_processed_data = cols + [player_link] +  [world_cup_link] +  [country_link]
                  data.append(your_processed_data)
        return data
    except Exception as error:
        print(error)
        return error

if __name__ == "__main__":
    player_list = []
    errors = []
    #  execution of the fuction with thread pool to avoid waiting time of the api for each call
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data, world_cup_link, country_link) for world_cup_link, country_link in country_appearances ]
    #  we iterate through the futures as they are completed
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if isinstance(result, list):
            player_list.extend(result)
        else:
            errors.append(result)

df_player_appearances = pd.DataFrame(player_list)
df_player_appearances.drop(columns= [0], axis=1, inplace=True)
df_player_appearances.columns=['minutes', 'appearances', 'starting_in', 'substitutions', 'replacements', 'goals','yellow_cards' , 'second_yellow', 'red_car', 'player_link', 'world_cup_link', 'country_link']
df_player_appearances.to_json(path_or_buf = f'{data_path}/appearances.json',orient='records')
  








    




