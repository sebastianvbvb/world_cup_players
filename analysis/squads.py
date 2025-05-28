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
from matplotlib import cm
from matplotlib.patches import Polygon
from pathlib import Path
# functions



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



from src.functions import set_age, bumpchart, calculate_triangule

from src.dataframes_for_analysis import load_dataframes

df_player, matchs, matchs_details, appearances = load_dataframes()





#  clubs, last  shows changes and see by federation. use 1/10 chain
# filter by top 4 and 8  finalista esta muy manchado
#
leagues_providers = df_player.loc[df_player.world_cup_year >= 2002]
first_5_leagues = leagues_providers.groupby('club_country')['link_player'].count().sort_values(ascending = False).head(5).index
leagues_providers = leagues_providers.pivot_table(index="club_country", columns="world_cup_year", values="link_player", aggfunc = 'count' )

plt.figure(figsize=(10, 5))
bumpchart(df = leagues_providers, to_rank = True , show_rank_axis= True,  value_format = 'value', scatter= True, holes= False, limit_rank = 5,
          line_args= {"linewidth": 5, "alpha": 0.5}, scatter_args= {"s": 500, "alpha": 0.8})

plt.title('The Leangues that provided more players since 2002')
plt.show()






# =============================================================================
# df_player.club_federation.unique()
# for f in df_player.club_federation.unique():
#     if isinstance(f , float) == False and f != 'OFC':
#         lg = df_player.loc[(df_player.world_cup_year >= 2002) & (df_player.club_federation == f)]
#         lg = lg.pivot_table(index="club_country", columns="world_cup_year", values="link_player", aggfunc = 'count' )
#         plt.figure(figsize=(10, 5))
#         bumpchart(df = lg, to_rank = True , show_rank_axis= True,  value_format = 'Value', scatter= True, holes= False, limit_rank = 5,
#                   line_args= {"linewidth": 5, "alpha": 0.5}, scatter_args= {"s": 800, "alpha": 0.8})
# 
#         plt.title('The Teams that provided more players since 2002')
#         plt.show()
# 
# =============================================================================


  # por federacion y pais ver deficits, ejemplo inglaterra aporta 100 y precisa 100, argentina aporta 4 y precisa 100.
df_player.columns
country_year  = df_player.groupby(['federation','world_cup_year']).agg(count=('link_player', 'count')).reset_index()   
club_year  = df_player.groupby(['club_federation','world_cup_year']).agg(count=('link_player', 'count')).reset_index()   
federation_balance = country_year.merge(club_year, left_on = ['federation', 'world_cup_year'], right_on = ['club_federation', 'world_cup_year'], suffixes = ('_country','_club') )
federation_balance.drop(columns = ['club_federation'], inplace = True)
federation_balance['balance'] = federation_balance.count_club - federation_balance.count_country 


plt.figure() 
fig, ax = plt.subplots(5, 1, sharex=True, sharey=False, figsize=(10, 15))
ax = ax.flatten()
federation_wo_ofc = ['UEFA', 'CONMEBOL', 'AFC', 'CAF', 'CONCACAF']


             

for f in federation_wo_ofc:
    data = federation_balance.loc[federation_balance.world_cup_year >= 1950]
    ind = federation_wo_ofc.index(f)
    data = data.loc[data.federation == f]
    ax[ind].bar(data.world_cup_year, data.count_country, alpha=0.5, color='blue', label='required')
    ax[ind].bar(data.world_cup_year + 1, data.count_club, alpha=0.5, color='green', label='provided')
    ax[ind].bar(data.world_cup_year+ 2 , data.balance , alpha=0.5, color='orange', label='balance')
    ax[ind].set_xticks(range(1950,int(df_player['world_cup_year'].max() + 8 - df_player['world_cup_year'].max() % 8 + 1), 8))
    ax[ind].set_title(f, color = 'black', loc = 'center')
    ax[ind].grid( axis = 'y')

ax[0].legend(['required', 'provided', 'balance'], ncol= 3)
fig.subplots_adjust(hspace=0.5)
fig.suptitle('Volume of players required and provided by federation', size = 'large', c = 'black', weight = 'extra bold')
fig.show()



player_participations = df_player.groupby('link_player').size().value_counts(normalize=False).to_dict()
# player_participations = pd.DataFrame.from_dict(player_participations, orient='index', columns = ['participations'])
player_participations

colours = cm.Set3(np.linspace(0, 1, len(player_participations)))


# player_participations = { 1: 60, 2 : 20, 3 : 15,  4 : 5}



sum(player_participations.values())
pyramid_base = 20 
pyramid_height = 10
ratio_pyramid = (pyramid_height / pyramid_base)
cumulative_percentage = 0
base_previous , height_previous = 0 ,0
fig, ax = plt.subplots(1,1)
jump = 0.15 # space between levels
alpha = 0.005 # vector for standarization. 
reversed(player_participations.items())

for i, (k,v) in enumerate(reversed(player_participations.items())):
    if alpha == 0:
        percentage = v / sum(player_participations.values())
    elif alpha > 0:
        dict_mean = sum(player_participations.values()) / len(player_participations)
        percentage =(v+ (dict_mean - v) * alpha) / sum(player_participations.values()) 
    print(percentage)
    cumulative_percentage = percentage + cumulative_percentage
    base , height =  calculate_triangule(pyramid_base, pyramid_height,cumulative_percentage)
    base = base + jump * ratio_pyramid
    # height_previous = height_previous - jump 
    jump_y_k = jump * (len(player_participations) - 1 - i)
    jump_x_k = jump * i
    if i ==0: #top (pyramid)
        xy0 = (pyramid_base / 2 -  base / 2   , pyramid_height - height + jump_y_k  )
        xy1 = (pyramid_base /2  , pyramid_height + jump_y_k)
        xy2 = (pyramid_base / 2 +  base / 2  , pyramid_height - height + jump_y_k)
        polygonk = Polygon([xy0, xy1, xy2],closed=True, facecolor=colours[i], label = f'{k}: {v} ({percentage:.1%})'  )
    elif i != 0: # trapezoid   
        xy0 = (pyramid_base / 2 -  base / 2 - jump_x_k    , pyramid_height - height + jump_y_k)        
        xy1 = (pyramid_base / 2 -  base_previous / 2 - jump_x_k , pyramid_height - height_previous +  jump_y_k) 
        xy2 = (pyramid_base / 2 +  base_previous / 2  + jump_x_k , pyramid_height - height_previous + jump_y_k)
        xy3 = (pyramid_base / 2 +  base / 2 + jump_x_k   , pyramid_height - height + jump_y_k)
        polygonk = Polygon([xy0, xy1, xy2, xy3],closed=True, facecolor=colours[i], label = f'{k}: {v} ({percentage:.1%})' )
        print([xy0, xy1, xy2, xy3]) 
    ax.add_patch(polygonk)
    base_previous , height_previous =  base , height

    

ax.set_xlim(-5, 25)  # Set x-axis limits
ax.set_ylim(0, pyramid_height + ( len(player_participations)  ) * jump )  # Set y-axis limits
plt.xticks([])
plt.yticks([])
plt.legend()
plt.title('World Cup Participations by a Player')
plt.show()


# legend
# legend inside, next, normal outside
