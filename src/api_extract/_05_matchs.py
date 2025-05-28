


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




# FUNCTIONS
# the scores by each time (including extra time and penalties)
def scores_times(x):
    pattern = r'(\d+:\d+)'
    scores = re.findall(pattern, x)    
    return scores

# reconizce who one the match. 
def victory(x):
    pattern = r'(\d+)'
    scores = re.findall(pattern, x)    
    local_victory = scores[0] > scores[1] 
    visitant_victory = scores[0] < scores[1] 
    return [local_victory, visitant_victory] #  list with boolean

# obtain how many goles scored each team
def goals(penalties, scores):
    if penalties ==True:
        goals = scores[-1].split(':')
    else:
        goals = scores[0].split(':')
    return [goals[0], goals[1]] #  list with int

# the minute the goals was done, excluding adding time
def minute_goal_limited(x):
    m = int(re.search(r'(\d+)\.', x).group(1))
    return int(m)

def minute_goal(x):
    m = int(re.search(r'(\d+)\.', x).group(1))
    if '+' in x:
        m = m + int( re.search(r'\+(\d+)', x).group(1))
    return int(m)
# how the goal was done (left,right, penalty,head)
def how(x):
    h = re.search(r'\/\s*([^()]+)\s*\(', x)
    if h:
       return h.group(1).strip()
    else:
       return None


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
# list of world cups. wotj ma,e amd accpromd to link

with open(f'{data_path}/countries.json', 'r') as f:
    countries  = json.load(f)
    countries_inverted = dict(zip(countries.values(), countries.keys()))
    

# folder to save/read data collected
start_time = datetime.now().time()    
 
matchs = []
start_time = datetime.now().time()    
for world_cup_link, world_cup in world_cups.items():
    print (world_cup_link)
    
    try:
        # the format of the url for the semifinal of a cup
        # example url = f'https://www.worldfootball.net/schedule/wm-2022-in-katar-halbfinale/0/'
        url = f'https://www.worldfootball.net/schedule/{world_cup_link}-halbfinale/0/'        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # the page contain a option feature to select the any other phase (name and link reference for the url)
        selection = soup.find('select', {'name': 'phase'})  
        options = selection.find_all('option')
        phases = [[option.text ,option['value']]  for option in options]
        #  example of a value in phases ['Group 1', '/schedule/wm-1930-in-uruguay-gruppe-1/0/']
        for phase in phases: 
            # similar to previous url but altering the phase as well
            url = f'https://www.worldfootball.net{phase[1]}'
            api = requests.get(url)
            api.raise_for_status()  # Raise HTTPError for bad responses
            soup = BeautifulSoup(api.text, 'lxml')
            table = soup.find('table', class_='standard_tabelle').find_all('tr')        
            for row in table:
                cols = row.find_all(['td'])            
                cols = [col.get_text(strip=True) for col in cols]     
                links = row.find_all('a')       
                match_link = links[2]['href'] if links else None                    
                # insertion of information into matchs list
                matchs.append(cols + [match_link] + [world_cup_link] + [phase[0]])
                
    except:
        pass
          
df_matchs =  pd.DataFrame(matchs)
# we drop columns not desired from row.find_all(['td'])
df_matchs.drop(columns= [3,6], axis=1, inplace=True)
df_matchs.columns = ['match_date', 'match_time', 'local_team', 'visitor_team','scores','match_link', 'world_cup_link', 'phase']
#  we remove rows without match information
df_matchs = df_matchs.dropna(subset = ['match_link'])
df_matchs['local_team_link'] = df_matchs['local_team'].map(countries_inverted)
df_matchs['visitor_team_link'] = df_matchs['visitor_team'].map(countries_inverted)
df_matchs = df_matchs.drop(columns = ['local_team','visitor_team'])
df_matchs.reset_index(drop=True, inplace = True)
df_matchs.phase = df_matchs.phase.apply(lambda x: x.replace('Final round', 'Final').replace('3rd place', 'Third place'))
# in origin when more than one match per day (same phase) only the first row contain date
for index, row in df_matchs.iterrows():
    if row['match_date'] =='':
        df_matchs.iloc[index,0] = df_matchs.iloc[index- 1,0] 


# identification whether there were penalties in the match
df_matchs['penalties'] = df_matchs['scores'].apply(lambda x: True if 'pso' in x else False )
# identification whether there was extra time in the match
df_matchs['extra_time'] = df_matchs['scores'].apply(lambda x: True if 'aet' in x else False )
# is local/vistan won ?
df_matchs['local_victory'], df_matchs['visitan_victory'] = zip(*df_matchs['scores'].apply(lambda x: victory(x)))
df_matchs['scores'] = df_matchs['scores'].apply(lambda x: scores_times(x))
#  goals scored by the local and visitan
df_matchs['local_goals'], df_matchs['visitan_goals'] = zip(*df_matchs.apply(lambda x: goals(x['penalties'], x['scores']), axis= 1 ))

# df_matchs.to_excel('match.xlsx')
df_matchs.to_json(path_or_buf = f'{data_path}/match.json',orient='records')


def process_match(match_link):
    # the format of the url of a match
    # example https://www.worldfootball.net/report/wm-1994-in-den-usa-achtelfinale-spanien-schweiz/
    url = f'https://www.worldfootball.net{match_link}'
# =============================================================================
#     if int(re.findall(r'\d+', match_link)[0])>= 2006:
#         liveticker = True
#         url = f'https://www.worldfootball.net{match_link}liveticker/'
#     else:
#         liveticker = False
#         url = f'https://www.worldfootball.net{match_link}'
# =============================================================================
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    selection = soup.find_all('table', {'class': 'standard_tabelle'})
# =============================================================================
#     if liveticker == True:
#             full_time = None
#             for table in selection:
#                 for row in table.find_all('tr'):
#                     cols = row.find_all(['td'])     
#                     cols = [col.get_text(strip=True) for col in cols]    
#                     if 'Full-Time' in cols:    
#                         full_time =cols[0]  
#                     elif 'Match over' in cols:                              
#                         full_time =cols[0] 
#                     else:
#                           for v in cols:
#                             if 'Full-Time' in v:                        
#                                   full_time =cols[0] 
# =============================================================================
    for table in selection:
            if table.find('tr').get_text(strip=True) == 'goals':
                for row in table.find_all('tr'):
                    # we process only rows with goals
                    if row.get_text(strip=True) not in ['goals', 'none']:
                        cols = row.find_all(['td'])
                        cols = [col.get_text() for col in cols]
                        links = row.find_all('a')    
                        player_link = links[0]['href'] if links else None
                        matchs_scores.append(cols + [player_link] +  [match_link])
# =============================================================================
#                         if liveticker:     
#                             try:
#                                 matchs_scores.append(cols + [player_link] +  [match_link] + [full_time])
#                             except Exception as error:
#                                 print(error)
#                                 print(match_link)
#                         else:
#                             matchs_scores.append(cols + [player_link] +  [match_link])
# 
# =============================================================================
                      
  


# Assuming df.match_link is a list of match links
match_links = df_matchs.match_link.tolist()
matchs_scores = []

#  execution of the fuction with thread pool to avoid waiting time of the api for each call
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_match, match_links)
    
    
    


df_matchs_scores = pd.DataFrame(matchs_scores)
df_matchs_scores.columns = ['new_score', 'goal_detail', 'player_link', 'match']

df_matchs_scores['minute'] = df_matchs_scores.goal_detail.apply(lambda x: minute_goal(x))
# limit to origin final time, adding time not consider (e.g 90+2 is 90 instead of 90)
df_matchs_scores['minute_limited'] = df_matchs_scores.goal_detail.apply(lambda x: minute_goal_limited(x))
df_matchs_scores['how'] = df_matchs_scores.goal_detail.apply(lambda x: how(x))

df_matchs_scores.to_json(path_or_buf = f'{data_path}/df_matchs_scores.json',orient='records')


# https://www.worldfootball.net/report/wm-2022-in-katar-finale-argentinien-frankreich/liveticker/
# =============================================================================
# 
# matchs_scores = []
# url = f'https://www.worldfootball.net/report/wm-2022-in-katar-finale-argentinien-frankreich/liveticker/'
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')
# selection = soup.find_all('table', {'class': 'standard_tabelle'})
# 
# for table in selection:
#     for row in table.find_all('tr'):
#         cols = row.find_all(['td'])            
#         cols = [col.get_text(strip=True) for col in cols]    
#         if 'Full-Time' in cols:
#             full_time =cols[0]
#     if table.find('tr').get_text(strip=True) == 'goals':
#         for row in table.find_all('tr'):
#               # we process only rows with goals
#               if row.get_text(strip=True) not in ['goals', 'none']:
#                   cols = row.find_all(['td'])
#                   cols = [col.get_text() for col in cols]
#                   links = row.find_all('a')
#                   player_link = links[0]['href'] if links else None
#                   matchs_scores.append(cols + [player_link] )
#               
# =============================================================================
  
    
  
    