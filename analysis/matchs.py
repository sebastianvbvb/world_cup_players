#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 21:47:06 2023

@author: sebastian
"""


# libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
from pathlib import Path
from pywaffle import Waffle

from collections import Counter
from pywaffle import Waffle
import matplotlib.pyplot as plt

from src.functions import set_age, bumpchart,  create_circle
from src.dataframes_for_analysis import load_dataframes


# Starting from current working directory
current_path = Path.cwd()


# Target folder name
project_name = 'world_cup_players'

# Look for the project folder in the path
if project_name in current_path.parts:
    index = current_path.parts.index(project_name)
    project_root = Path(*current_path.parts[:index + 1])
    data_path = project_root / 'data' / 'raw' / 'json'
    functions_path = project_root / 'src'

else:
    raise ValueError(f"'{project_name}' not found in path")





df_player, matchs, matchs_details, appearances = load_dataframes()



# sns.stripplot(data = matchs_details, x = 'phase' , y ='minute_limited', hue ='world_cup_year'  ,palette="deep")
matchs_details['bin_minute'] = pd.cut(x=matchs_details['minute_limited'], bins=range(0,121,5), labels= [f"{i}-{i+5}" for i in range(0, 116, 5)]  )

plt.figure() 
sns.histplot(data=matchs_details.loc[matchs_details.phase != 'Third place'], x="bin_minute", hue="phase", multiple="stack")
plt.axvline(x=8.5, color='grey', linestyle='--', linewidth=2)
plt.axvline(x=17.5, color='grey', linestyle='--', linewidth=2)
#  add a tag label with subtotal by half 
plt.title('Goals by Minute and Phase', size = 'medium', c = 'black', weight = 'bold')
#plt.legend(matchs_details.loc[matchs_details.phase != 'Third place'].phase.unique(), fontsize = 'small', loc='upper right')
plt.xlabel("Minute of Match")
plt.ylabel("Goals")
plt.show()

 
goal_how_group = {'header' : 'header', 'left-footed shot' : 'left-footed', 'right-footed shot' : 'right-footed', 'penalty' : 'penalty'
,'free kick' : 'free kick', 'own goal' : 'own goal' , 'bicycle kick' : 'other', 'back heel' : 'other',
       'ind. free kick' : 'other'} 

matchs_details.how = matchs_details.how.map(goal_how_group)
# plt.figure() 
# sns.histplot(data=matchs_details.loc[matchs_details.world_cup_year >= 1998] , x="bin_minute", hue="how", multiple="fill")
# plt.axvline(x=8.5, color='grey', linestyle='--', linewidth=2)
# plt.axvline(x=17.5, color='grey', linestyle='--', linewidth=2)
# plt.xticks( range(0,23,2)) 
# #  add a tag label with subtotal by half 
# plt.title ('How Goals Were Scored')
# plt.xlabel("Minute of Match")
# plt.ylabel("Goals in Percentage")
# plt.show()


plt.figure() 
matchs_details['bin_minute'] = pd.cut(x=matchs_details['minute_limited'], bins=range(0,121,5), labels= [f"{i}-{i+5}" for i in range(0, 116, 5)]  )
sns.histplot(data=matchs_details.loc[matchs_details.phase != 'Third place'], x="bin_minute", hue="how", multiple="stack")
plt.axvline(x=8.5, color='grey', linestyle='--', linewidth=2)
plt.axvline(x=17.5, color='grey', linestyle='--', linewidth=2)
#  add a tag label with subtotal by half 
plt.title ('How Goals Were Scored')
plt.xlabel("Minute of Match")
plt.ylabel("Goals")
plt.show()


matchs_details['foot_goal'] = matchs_details.how.apply(lambda x: x.replace('-footed', '') if x in ['left-footed','right-footed'] else None) 
pivot_goal = matchs_details.loc[(matchs_details.foot_goal.isnull() == False)].pivot_table(index="foot_goal", columns="foot", values="link_player", aggfunc = 'count', margins=True, margins_name = 'Total' )
print(pivot_goal)
print(f"{(pivot_goal.loc['right', 'left'] / pivot_goal.loc['Total', 'left']):.1%} of the right-footed goals were done by made by left-foot players" )
print(f"{(pivot_goal.loc['left', 'right'] / pivot_goal.loc['Total', 'right']):.1%} of the left-footed goals were done by made by right-foot players" )

# Pictorial Percentage Chart or Pictorial Fraction Chart with balls


plt.figure() 
sns.histplot(data = matchs_details.loc[matchs_details.how == 'header'] , x='height', binwidth = 1, hue = 'position' , multiple="stack")
plt.title('Headed Goals By Height and Position')
plt.xlabel("Height")
plt.ylabel("Goals")
plt.show()


# matchs_details.loc[matchs_details.how == 'own goal']['position'].value_counts().reset_index().rename(columns={'count': 'own goals'})  
# matchs_details.loc[matchs_details.how == 'free kick'][['position', 'foot']].value_counts()


count_teams = matchs.loc[matchs.world_cup_year >= 1998][['local_country','visitor_country']] 
count_teams = len(set(count_teams['local_country'].unique()) | set(count_teams['visitor_country'].unique()))

count_teams_16 = matchs.loc[(matchs.world_cup_year >= 1998) & (matchs.phase == 'Round of 16')][['local_country','visitor_country']] 
count_teams_16 = len(set(count_teams_16['local_country'].unique()) | set(count_teams_16['visitor_country'].unique()))

count_teams_quater = matchs.loc[(matchs.world_cup_year >= 1998) & (matchs.phase == 'Quarter-finals')][['local_country','visitor_country']] 
count_teams_quater = len(set(count_teams_quater['local_country'].unique()) | set(count_teams_quater['visitor_country'].unique()))

count_teams_semi= matchs.loc[(matchs.world_cup_year >= 1998) & (matchs.phase == 'Semi-finals')][['local_country','visitor_country']] 
count_teams_semi = len(set(count_teams_semi['local_country'].unique()) | set(count_teams_semi['visitor_country'].unique()))


count_teams_final = matchs.loc[(matchs.world_cup_year >= 1998) & (matchs.phase == 'Final')][['local_country','visitor_country']] 
count_teams_final =len( set(count_teams_final['local_country'].unique()) | set(count_teams_final['visitor_country'].unique()))


max_position_dict  = {
    'Final' : count_teams_final, 
    'Semi-finals' : count_teams_semi - count_teams_final, 
    'Quarter-finals' : count_teams_quater - count_teams_semi, 
    'Round of 16' : count_teams_16 - count_teams_quater, 
    'Groups' : count_teams - count_teams_16
    } 
max_position_dict



# Data
value = list(max_position_dict.values())[::-1]
color = [ "#ffd003", "#d7d7d7", "#ADD8E6", "#90EE90", '#FF6666'][::-1]
# color = [ "gold", "silver", "blue", "green", 'red']

# Waffle chart
plt.figure(
    FigureClass = Waffle,
    # rows = max_position_dict['Final'] + max_position_dict['Semi-finals'] ,
    columns = max(max_position_dict['Final'], math.ceil((max_position_dict['Groups'] / 4)))   ,
    values = value,
    colors = color,
    rounding_rule='floor',
    icons = 'award',
    icon_legend = True,
    vertical=True,
    block_arranging_style='new-line',
    legend = {
        'labels': [f'{k} ({v})' for k,v in  max_position_dict.items()][::-1]  , # list(max_position_dict.keys()), 
        'loc': 'upper left', 
        'bbox_to_anchor': (1, 1)
        },
    title = {"label": "Best Performance by Countries Since France 1998", "loc": "center", "size": 12})
plt.show()


count_federation_quater = matchs.loc[(matchs.world_cup_year >= 1998) & (matchs.phase == 'Quarter-finals')][['local_federation','visitor_federation']] 

quater_federations_participations = Counter(list(count_federation_quater['local_federation']) + list(count_federation_quater['visitor_federation']))
quater_federations_participations['UEFA']




# Data
value = {'UEFA':quater_federations_participations['UEFA'],'Rest' : sum(quater_federations_participations.values()) - quater_federations_participations['UEFA']}
color = [ "#3968A5", "#d7d7d7"]
# color = [ "#14223E", "silver", "blue", "green", 'red']

# Waffle chart
plt.figure(
    FigureClass = Waffle,
    rows = 1,
    columns = 10  ,
    values = value,
    colors = color,
    icons = 'person-running',
    font_size=30,
    rounding_rule='floor',
    icon_legend = True ,   
    legend = {
        'labels': ['UEFA', 'Rest'], 
        'loc': 'upper left', 
        'bbox_to_anchor': (1, 1)},
    vertical=True,
    title = {"label": "6 of 10 teams that played Quaters are from EUFA", "loc": "center", "size": 12}
    )
plt.show()



matchs['total_goals'] = matchs.local_goals + matchs.visitan_goals

plt.figure() 
sns.histplot(matchs, x = 'total_goals',discrete = True  )
plt.xticks(range(0, max(matchs.total_goals) , 1))
plt.title('Goals by Match - Historic')
plt.ylabel('Matches')
plt.xlabel('Goals')
plt.show()


# matchs.groupby('world_cup_year')['total_goals'].quantile(q = 0.5).plot( color = 'blue')

plt.figure() 

# Because of there is more than one mode in some years, we plot two lines that overlap in some years

average_goals = matchs.groupby('world_cup_year')['total_goals'].mean()
total_goals_mode = matchs.groupby('world_cup_year')['total_goals'].agg(lambda x: x.mode())

first_mode = [i[0] if isinstance(i, np.ndarray) else i for i in total_goals_mode]
second_mode = [i[1] if isinstance(i, np.ndarray) else i for i in total_goals_mode]
plt.plot( sorted(list(matchs.world_cup_year.unique())) ,  average_goals, color = 'green', label = 'average')
plt.plot( sorted(list(matchs.world_cup_year.unique())) ,  first_mode, color = 'red', label = 'mode')
plt.plot( sorted(list(matchs.world_cup_year.unique())) ,  second_mode, color = 'red')
plt.grid()
plt.legend()
plt.xticks(range(1930,int(df_player['world_cup_year'].max() + 8 - df_player['world_cup_year'].max() % 8 + 1), 8))
plt.xlabel( None)
plt.title('Goals by Year - Averange and Mode')
plt.show()

player_scores = matchs_details.groupby('link_player').size().value_counts(normalize=False).to_dict()
player_scores_short = {'1': 0, '2-3': 0, '4-6': 0, '7-10': 0, '+10': 0}
for key, value in player_scores.items():
    if key == 1:
        player_scores_short['1'] += value
    elif 2 <= key <= 3:
        player_scores_short['2-3'] += value
    elif 4 <= key <= 6:
        player_scores_short['4-6'] += value
    elif 7 <= key <= 10:
        player_scores_short['7-10'] += value
    else:
        player_scores_short['+10'] += value
        
        
        
player_scores = matchs_details.groupby('link_player').size().value_counts(normalize=False).to_dict()
player_scores_short = {'1': 0, '2-3': 0, '4-6': 0, '7-10': 0, '+10': 0}
for key, value in player_scores.items():
    if key == 1:
        player_scores_short['1'] += value
    elif 2 <= key <= 3:
        player_scores_short['2-3'] += value
    elif 4 <= key <= 6:
        player_scores_short['4-6'] += value
    elif 7 <= key <= 10:
        player_scores_short['7-10'] += value
    else:
        player_scores_short['+10'] += value
        
      
        
df = appearances.loc[appearances.world_cup_year == 2022]
country_matchs_played_dict = df.groupby('country')['appearances'].max().to_dict()
df['played'] =  df['appearances'].apply(lambda x: x > 0)

country_count = len(df.country.unique())
max_number_players = max(df.groupby('country').size())

      
country_count = len(df.country.unique())
max_number_players = max(df.groupby('country').size())


appearances_list = df.groupby('country')['played'].apply(lambda x:  list(x.value_counts()) ).to_dict()
appearances_list = dict(sorted(appearances_list.items(), key=lambda item: country_matchs_played_dict[item[0]]))

sorted_dict = dict(sorted(appearances_list.items(), key=lambda item: item[1]))
print(appearances_list)
for k, v in appearances_list.items():
    country_players_played = v[0]
    country_players_not_played = v[1] if len(v) ==2 else 0
    fewer_players = max_number_players - (country_players_played + country_players_not_played) 
    appearances_list[k] =  [ country_players_played , country_players_not_played , fewer_players]

appearances_list_chain = [i for l in list(appearances_list.values()) for i in l]


# Data
value = appearances_list_chain
color = ["white", "#d7d7d7", "#ffd003" ] * country_count 


# Waffle chart
plt.figure(
    FigureClass = Waffle,
    rows = max_number_players,
    columns = country_count,
    values = list(reversed(value)),
    colors = color,
    rounding_rule='floor',
    legend = {
        'labels': ['Player','Did not Play','Played'] , # list(max_position_dict.keys()), 
        'loc': 'upper left', 
        'bbox_to_anchor': (1, 1)
        },
    title = {"label": "Appearances of Players by Teams - Qatar 2022", "loc": "center", "size": 12})
plt.show()


# colours = cm.Set3(np.linspace(0, 1, len(player_scores_short)))


# center_location  = np.array((10,10))
# slope_vector = np.array((1,-2))
# biggest_radius = 10 
# top_value = max(player_scores_short.values())

# max_number_players = max(df.groupby('country').size())

