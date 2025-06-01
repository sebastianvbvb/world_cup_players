# libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import os
import json
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
    


# fuction to get the players from a combination of world cup and country
def fetch_data(country, country_link, world_cup, world_cup_link):
    world_cup_link = world_cup_link.replace('/players','')
    try:
        # the format of the url that shows the squad of the country in specific cup
        #  example https://worldfootball.net/teams/kanada-team//wm-2022-in-katar/2/
        url = f'https://worldfootball.net{country_link}{world_cup_link}2/'
        api = requests.get(url)
        soup = BeautifulSoup(api.text, 'lxml')
        table = soup.find('table', class_='standard_tabelle').find_all('tr')
        data = []
        position = None # a variable for invidual assignation of position in the field
        for row in table:
            try:
                # the website split the table by position but does not assign the possition to each player, only to title before players.
                # we obtain the position from previous row until next position appear
                if row.find_all(['th'])[0].get_text() in ['Goalkeeper','Defender','Midfielder', 'Forward']:
                    position = row.find_all(['th'])[0].get_text()
                # several squads contain manager and assitances that are not looked for this project
                elif row.find_all(['th'])[0].get_text() in ['Manager','Ass. Manager']:
                    break 
                else:
                    pass
            except IndexError:
                pass  #  only few rows contain th, it is expect indexerror when we use [0] in almost all rows
            except Exception as error:
                error
            cols = row.find_all(['td'])
            cols = [col.get_text(strip=True) for col in cols] # to comment
            #We get the api of the player to get more information further. 
            # It will be used as id as well because of existence of duplication with names).
            links = row.find_all('a')
            href_link = links[0]['href'] if links else None
            # the country of the club he was playing at the moment of the world cup.
            images = row.find_all('img')
            club_country = [i['title'] for i in images if 'flaggen' in i['src']]
            # club_country is not converted from list to string as some players do not registered club return as empty string. 
            # we avoid double processing later otherwise
            
            # we join all data and append to the list 
            row_data = cols + [href_link] + club_country + [country_link] + [world_cup_link] + [position]
            
            data.append(row_data)
        return data
    except Exception as error:
        print(error)
        return error

if __name__ == "__main__":
    player_list = []
    errors = []
    #  we run the function over a for loop by world cups. 
    for world_cup_link, world_cup in world_cups.items():
        loop_start_time = datetime.now().time() # for live controlling during the execution
        print(world_cup_link)
        #  execution of the fuction with thread pool to avoid waiting time of the api for each call
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # the threads is apply by country (within same world_cup)
            futures = [executor.submit(fetch_data, team, link_team, world_cup, world_cup_link) for team, link_team in countries.items() ]
        #  we iterate through the futures as they are completed
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if isinstance(result, list):
                player_list.extend(result)
            else:
                errors.append(result    )
        loop_end_time = datetime.now().time()    # Replace with your actual end time
        time_difference = datetime.combine(datetime.today(), loop_end_time) - datetime.combine(datetime.today(), loop_start_time)
        minutes_difference = time_difference.total_seconds() / 60 
        print(f"Time difference: {minutes_difference}")
        time.sleep(1)
 



df_player = pd.DataFrame(player_list)
# we drop columns not desired from row.find_all(['td'])
df_player.drop(columns= [0,3], axis=1, inplace=True) 
df_player.columns=['jersey', 'name', 'club', 'birth_date', 'link_player', 'club_country', 'country_link','world_cup_link' , 'position']
#  we remove rows without player information
df_player = df_player.dropna(subset = ['link_player'])
df_player.to_json(path_or_buf = f'{data_path}/squads.json',orient='records')
  



    


    




