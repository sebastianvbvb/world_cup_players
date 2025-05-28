#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 18 10:41:54 2025

@author: sebastian
"""

# libraries
import numpy as np
import matplotlib.pyplot as plt
from datetime import date as date
from dateutil.relativedelta import relativedelta
import math





# set age of the player, between birth and cup of the wolrd cup. 
def set_age(birth, cup_year):
    try:
        if isinstance(birth, float)  == False and birth != None:        
            cup_year = cup_year
            cup_date  = date(cup_year, 7, 1) # usually the world cups starts in june
            age = relativedelta(cup_date,birth).years
        else:
            age = np.nan
        return age
    except:
        pass
    
    
# return the base and height of triangule (or trapeze). Use to built a pyramid for distribution
def calculate_triangule(original_base , original_height, percentage ):    
    ratio_base_height = original_height / original_base
    original_area = (original_base * original_height) / 2
    new_base =  pow(original_area * percentage * 2 * 2, ratio_base_height)
    new_height =  new_base * ratio_base_height
    return new_base, new_height
# calculate_triangule(20, 10,0.4)


# return the center location and radi
def create_circle(proportion, center_location ,biggest_radius ,slope_vector ):
    new_radius = math.sqrt(proportion) * biggest_radius
    angle_in_radians  = math.atan2(slope_vector[1], slope_vector[0])
    border_x1 = center_location[0] + (biggest_radius - new_radius) * math.cos(angle_in_radians)
    border_y1 = center_location[1] + (biggest_radius - new_radius) * math.sin(angle_in_radians)
    new_center = np.array((border_x1,border_y1))     
    return new_center,new_radius






# bumchapt for changes in ranking
def bumpchart(df, to_rank = False,limit_rank= 7, show_rank_axis= True, rank_axis_distance= 1.1, ax= None,
              scatter= False, holes= False,value_format = None,
              line_args= {}, scatter_args= {}, hole_args= {}):
    
    # to be used for text values
    original_df = df.copy()
    # if df contains original measure, we convert it as ranking table
    if to_rank == True:
        df = df.rank(axis = 0, ascending = False, method = 'first')
        df = df.applymap(lambda x: int(x) if math.isnan(x) == False else x )
        df = df.loc[df.min(axis = 1) <= limit_rank]
        df = df.T
    
    if ax is None:
        left_yaxis= plt.gca()
    else:
        left_yaxis = ax

    # Creating the right axis.
    right_yaxis = left_yaxis.twinx()
   
    axes = [left_yaxis, right_yaxis]
   
    # Creating the far right axis if show_rank_axis is True
    if show_rank_axis:
        far_right_yaxis = left_yaxis.twinx()
        far_left_yaxis = left_yaxis.twinx()
        axes.append(far_right_yaxis)
        axes.append(far_left_yaxis)

    for col in df.columns:
        y =  df[col]
        x = df.index.values
        # Plotting blank points on the right axis/axes
        # so that they line up with the left axis.
        for axis in axes[1:]:
            axis.plot(x, y, alpha= 0)

        left_yaxis.plot(x, y, **line_args, solid_capstyle='round')
       
        # Adding scatter plots
        if scatter:
            left_yaxis.scatter(x, y, **scatter_args)
           
            #Adding see-through holes
            if holes:
                bg_color = left_yaxis.get_facecolor()
                left_yaxis.scatter(x, y, color= bg_color, **hole_args)

    if value_format == 'ranking':
        for column, serie in df.items():
            for index, ranking in serie.items():
                left_yaxis.text(index,
                ranking,
                '{:n}'.format (ranking),
                fontsize=7)  # Rotate the              

    elif value_format == 'value':
        if to_rank == False:
            print('only works with to_rank')
        else:
            for column, serie in df.items():
                for index, ranking in serie.items():
                    value = original_df.loc[column][index]
                    left_yaxis.text(index,
                                    ranking,
                                    '{:n}'.format(value),
                                    fontsize=7) #
    elif value_format == 'participation':
        if to_rank == False:
            print('only works with to_rank')
        else:
            for column, serie in df.items():
                df_participation = original_df.div(original_df.sum(axis = 0))
                for index, ranking in serie.items():
                    value = df_participation.loc[column][index]
                    left_yaxis.text(index - 0.007,
                                    ranking,
                                    '{:.1%}'.format(value),
                                    fontsize=7) 

   
    # Number of lines
    lines = len(df.columns)
   
    y_ticks = [*range(1, lines + 1)]
   
    # Configuring the axes so that they line up well.
    for axis in axes:
        axis.invert_yaxis()
        axis.set_yticks(y_ticks)
        axis.set_ylim((limit_rank + 0.5, 0.5))
   
    # Sorting the labels to match the ranks.
    left_labels = df.iloc[0].sort_values().index
    right_labels = df.iloc[-1].sort_values().index
    left_yaxis.set_yticklabels(left_labels,  fontsize=8)  

    right_yaxis.set_yticklabels(right_labels ,  fontsize=8)    
    # left_yaxis.set_ylim(bottom = limit_rank + 0.5 )
    # right_yaxis.set_ylim(bottom = limit_rank + 0.5 )
   
    left_yaxis.set_xticks(x)
    left_yaxis.set_xticklabels(df.index.values,  fontsize=8)
    right_yaxis.set_xticks(x)
    right_yaxis.set_xticklabels(df.index.values,  fontsize=8)
   
   
    # Setting the position of the far right axis so that it doesn't overlap with the right axis
    if show_rank_axis:
        far_right_yaxis.spines["right"].set_position(("axes", rank_axis_distance))
        far_left_yaxis.spines["right"].set_position(("axes", -0.1))
        # far_left_yaxis.spines['left'].set_visible(False)
   
    return axes



