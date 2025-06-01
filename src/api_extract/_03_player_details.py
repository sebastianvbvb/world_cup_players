#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 16:21:43 2023

@author: sebastian
"""


# libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import json
import os 
import re
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
    
    
squads = pd.read_json(f'{data_path}/squads.json',orient='records')
squads.sort_values(by=['country_link'], inplace = True)

def set_date (x):
    if isinstance(x, float)  == False:
        new= re.findall(r'[0-9. ]+', x)
        new = ' '.join(new)
        new = new.lstrip()
        new = new.split(' ')[0]        
        if len(new) > 4:
                try:
                    datetime.strptime(new,'%d/%m/%Y').date()
                except:
                    new = datetime.strptime(new,'%d.%m.%Y').date()
        elif len(new) == 4:
            new = datetime.strptime(new,'%Y').date()
        else:
            new = np.nan

    else:
        new = np.nan
    return new





player_details = {}
count = 1 

def fetch_player_details(player):
    try:
        # the format of the url where is possible some personal details of player (height, foot, city of born)
        #  example https://www.worldfootball.net/player_summary/mo-salah/
        url = f'https://www.worldfootball.net/{player}' 
        api = requests.get(url)
        soup = BeautifulSoup(api.text, 'lxml')
        # table with personal details
        table = soup.find('table', class_='standard_tabelle yellow').find_all('tr')
        player_info = {}
        for row in table:
            field = row.find_all('b') # tag for field name
            if field: # to exclude undesired lines as picture and name
                field = field[0].get_text(strip=True).replace(':', '') 
                field_value = row.find_all('td')[1].get_text(strip=True) # value of the field
                player_info[field] = field_value # we assignt the field and value to the list
                
        count =+ 1 
        return player, player_info # 'player' used for assgination in dictionary
    except Exception as error:
        return player, {'error': str(error)}
    print(count)

player_details = {}
count = 1

# iteration over country list (by link)
for country_link in squads.country_link.unique(): 
    loop_start_time = datetime.now().time() #only for live controling
    print(country_link) 
    country_squad = squads.loc[squads.country_link == country_link]
    # extraction of unique players for the current country
    player_list = country_squad['link_player'].unique()
    
    #  execution of the fuction with thread pool to avoid waiting time of the api for each call
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_player_details, player_list))
        # insertion of information into player_details
        for player, player_info in results:
            player_details[player] = player_info
        
    except Exception as error:
        print(error)
        
    loop_end_time = datetime.now().time()    # Replace with your actual end time
    time_difference = datetime.combine(datetime.today(), loop_end_time) - datetime.combine(datetime.today(), loop_start_time)
    time_difference = int( time_difference.total_seconds() )
    print(f"Time difference: {time_difference} seconds")



# unique_fields = set(key for sub_dict in player_details.values() for key in sub_dict)






# list of details to dataframe
df_player_details = pd.DataFrame.from_dict(player_details, orient='index')
df_player_details.reset_index(names=['link_player'],inplace = True)
df_player_details.drop(columns = ['size of shoe','Homepage'])
column_rename = {'Born' :'born', 'Place of birth' : 'place_birth', 
                          'Nationality' : 'nationality', 'Height' : 'height', 'Weight' : 'weight',
                          'Position(s)' : 'position_multiple', 'Foot' :'foot','size of shoe' : 'shoe_size'}


df_player_details.rename(columns = column_rename, inplace = True)

df_player_details.born = df_player_details.born.apply(lambda x: set_date(x)) 
df_player_details.born = df_player_details.born.apply(lambda x: str(x) if  isinstance(x,float) == False else None) 

df_player_details.height = df_player_details.height.apply(lambda x: int(x.replace(' cm', '')) if isinstance(x, str)  else x)
df_player_details.weight = df_player_details.weight.apply(lambda x: int(x.replace(' kg', '')) if isinstance(x, str)  else x)

df_player_details.to_json(path_or_buf = f'{data_path}/df_player_details.json',orient='records')
