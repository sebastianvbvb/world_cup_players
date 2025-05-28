# libraries
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import requests
from bs4 import BeautifulSoup
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







# the url bellow contain all contries which have participated in the wolrd cup.
url = 'https://www.worldfootball.net/alltime_table/wm/'  
try:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    selection = soup.find('table', {'class': 'standard_tabelle'})  
    # look the links from the table that contains countries's references (link and name)  
    options = selection.find_all('a')
    countries =  {option['href'] : option.text   for option in options}
    print(countries)
    # del countries[''] # salvador appear once in blank
    
    with open(f'{data_path}/countries.json', 'w') as f: 
        json.dump(countries, f,  ensure_ascii=False, indent=2)
except Exception as error:
    print(error)
print (countries)





# api call of a section that contains a dropdown with all world cups as options.
url = 'https://www.worldfootball.net/players/wm-2022-in-katar/'  
try:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    selection = soup.find('select', {'name': 'saison'})  
    options = selection.find_all('option')
    option_list = [option.text for option in options]    
    print(option_list)
    world_cups = {option['value'].replace('/players','') : {'name' : option.text , 'year' :  int(option.text[:4])} for option in options}

    with open(f'{data_path}/world_cups.json', 'w') as f: 
        json.dump(world_cups, f,  ensure_ascii=False, indent=2)
except:
     pass


# a api call by every country to identify its federation
federations = {}
try:
    for link, name in countries.items():
        url = f'https://www.worldfootball.net{link}'
        print (url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        selection = soup.find('table', {'class': 'standard_tabelle yellow'})  # 
        lines = selection.find_all('img')
        federations[link] =  [line['title']  for line in lines][0]
    with open(f'{data_path}/federations.json', 'w') as f: 
        json.dump(federations, f)
except Exception as error:
    print(error)
    
    
    

