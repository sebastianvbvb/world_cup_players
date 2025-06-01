#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 21:47:06 2023

@author: sebastian
"""


# libraries
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path



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


from src.dataframes_for_analysis import load_dataframes
df_player, matchs, matchs_details, appearances = load_dataframes()

    
                
stats_by_country_year = df_player.groupby(['country', 'world_cup_year']).agg({'height': 'mean','weight': 'mean'}).reset_index()

first_cup = df_player.world_cup_year.min()
last_cup = df_player.world_cup_year.max()
# charts
# charectstics phisics
plt.figure() 
p = sns.histplot(df_player, x="height", hue="position", common_bins=False,element="step")
plt.grid(linestyle='dashed') #just add this
plt.xticks(range(int(df_player['height'].min() - df_player['height'].min() % 5) , int(df_player['height'].max() +  5 -  df_player['height'].max() % 5 + 1) , 5))
df_player.loc[df_player.height.isnull()  == False].world_cup_year.min()
plt.title(f'Height Count by Position ({first_cup} - {last_cup})')
plt.xlabel("Height (Cm)")
plt.ylabel("Number of Players")
plt.show()


plt.figure() 
p = sns.histplot(df_player, x="height", y = 'position',common_bins=False,  hue="position", legend = False )
plt.xticks(range(int(df_player['height'].min() - df_player['height'].min() % 5) , int(df_player['height'].max() +  5 -  df_player['height'].max() % 5 + 1) , 5))
plt.title(f'Height Concentration by Position ({first_cup} - {last_cup})')
plt.show()



height_resume = df_player.pivot_table(index="federation", columns="position", values="height", aggfunc={'height': ['mean', 'median']})
height_resume['mean'] = height_resume['mean'].round(1) 
height_resume['median'] = height_resume['median'].astype(int)
height_resume.rename(columns = {'mean' : 'mean height','median' : 'median height'}, inplace = True)

height_resume.sort_index(axis=1, level='position')
height_resume = height_resume.reorder_levels([1, 0], axis=1)
height_resume = height_resume.reindex(columns=['Goalkeeper','Defender','Midfielder','Forward'], level='position') 
print (height_resume)



#  age 
# IF i want to add avg?
plt.figure() 
p = sns.lineplot(data=df_player, x="world_cup_year", y="age",hue="position",  estimator=np.median, style="position",ci=None)
plt.xticks(range(int(df_player['world_cup_year'].min() ), int(df_player['world_cup_year'].max() +  8 -  df_player['world_cup_year'].max() % 8 + 1) , 8))
plt.title(f'Age by Position - Median ({first_cup} - {last_cup})')
plt.xlabel("World Cup Year")
plt.ylabel("Age")
plt.show()

# =============================================================================
# p = sns.lineplot(data=df_player, x="world_cup_year", y="age",hue="position",  estimator=np.mean, style="position",ci=None)
# plt.xticks(range(int(df_player['world_cup_year'].min() ), int(df_player['world_cup_year'].max() +  8 -  df_player['world_cup_year'].max() % 8 + 1) , 8))
# plt.title(f'Age by Position - Mean ({first_cup} - {last_cup})')
# plt.show()
# 
# =============================================================================
plt.figure() 
p = sns.lineplot(data=df_player, x="world_cup_year", y="age",hue="federation",  estimator=np.median, style="federation",ci=None)
plt.xticks(range(int(df_player['world_cup_year'].min() ), int(df_player['world_cup_year'].max() +  8 -  df_player['world_cup_year'].max() % 8 + 1) , 8))
plt.title(f'Age by Federation - Median ({first_cup} - {last_cup})')
plt.xlabel("World Cup Year")
plt.ylabel("Age")
plt.show()
# =============================================================================
# 

# 
# =============================================================================


# foot
plt.figure() 
last_3w_foot = df_player.loc[df_player.world_cup_year >= df_player['world_cup_year'].max() - 8]
last_3w_foot = last_3w_foot.pivot_table(index="position", columns="foot", values="link_player", aggfunc = 'count' )
last_3w_foot =  last_3w_foot.div(last_3w_foot.sum(axis= 1), axis=0) * 100 
last_3w_foot.plot(kind = 'bar', stacked = True,mark_right = True)
plt.title(label = 'Foot by Position - Last 3 world cups')
plt.ylabel(ylabel = 'Percentage (%)')
plt.xlabel(xlabel = None)
for index, row in last_3w_foot.reset_index(drop=True).iterrows():
    for column in row:
        plt.text(index,column ,f"{column / 100: .1%}",
                va="center",ha="center")
   
            
plt.legend(loc ='center right')




