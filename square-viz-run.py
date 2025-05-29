#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 06:38:29 2024

@author: chamomile
"""
from pathlib import Path, PurePath
import re

import cv2

from visualization.visualization import Visualization

from helpers.roi_manip import convert_to_contours

from helpers.centroid_manip import generate_row_col
import pandas as pd

from collections import Counter

import numpy as np

#filepath = '/home/chamomile/Thyme-lab/data/hpc/csv/'

filepath = "/home/chamomile/Thyme-lab/data/vids/social_and_many_well/"

all_ages = {}
age_list = [PurePath(f).name for f in Path(filepath).iterdir() if f.is_dir()]
age_list.sort(key=lambda test_string: list(
    map(int, re.findall(r'\d+', test_string)))[0])

print(age_list)
v = Visualization(["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"],  [
                  "LLLL", "RRRR", "LLLR", "RRRL", "LLRR", "RRLL", "LRRR", "RLLL", "RLLR", "LRRL", "RRLR", "LLRL", "LRLR", "RLRL", "LRLL", "RLRR"], 4, age_list, "viridis")

percents = {}

ages_enum = range(0, len(age_list))

base_fp = "/home/chamomile/Thyme-lab/data/vids/social_and_many_well/fc2_save_2025-01-13-171831-0000-examine"
data_fp = base_fp +"post-processed.csv"
movie_fp = base_fp + ".avi"
mode_noblur_path = base_fp + "-mode.png"

vidcap = cv2.VideoCapture(movie_fp)

frame_width = int(vidcap.get(3))
frame_height = int(vidcap.get(4))

cell_contours, contour_mask, cell_centers = convert_to_contours(base_fp+".cells", frame_width, frame_height)
mode_noblur_img = cv2.cvtColor(cv2.imread(mode_noblur_path), cv2.COLOR_BGR2GRAY)

shape_of_rows = [len(cell_centers[row]) for row in range(len(cell_centers))]
num_rows = len(shape_of_rows)


"""tetragrams"""
def match(turn_map_indiv):
    """Create sets of four based on turn map."""
    sets_of_four = []

    for i in range(0, len(turn_map_indiv) - (v.NUMBER_OF_DIVISIONS - 1)):
        sets_of_four.append(turn_map_indiv[i:i + v.NUMBER_OF_DIVISIONS])

    return sets_of_four

def match_sets_of_four(self, turn_map):
    """Run match for each of the cells."""
    sets_of_four = []

    num_rows = len(shape_of_rows)
    for row in range(num_rows):
        num_cols = shape_of_rows[row]
        for col in range(num_cols):
            l = turn_map[row][col]
            sets_of_four.extend(match(l))

    return sets_of_four

def count(sets_of_four):
    """Count tetragrams and create percentage of each kind of tetragram."""
    counter = Counter(sets_of_four)
    combin_counter = {l: 0 for l in v.labels}

    for l in v.labels:
        for val in counter.keys():
            if val in l:
                combin_counter[l] += counter[val]

    percent = 100 * np.array(list(combin_counter.values())
                             ) / sum(combin_counter.values())

    return percent

def convert_to_quadrant(pos_x: int, pos_y: int, row: int, col: int):
    center = cell_centers[row][col]
    
    if center[0] - 5 < pos_x < center[0] + 5:
        return None
    
    if center[1] - 5 < pos_y < center[1] + 5:
        return None
    
    if pos_y < center[1]:
        if pos_x < center[0]:
            return 0
        else:
            return 1
    else:
        if pos_x < center[0]:
            return 3
        else:
            return 2

def turn_l_r(prev_arm: int, curr_arm: int):
    if (prev_arm, curr_arm) == (0, 3):
        return "L"

    elif (prev_arm, curr_arm) == (3, 0):
        return "R"

    elif prev_arm < curr_arm:
        return "R"

    else:
        return "L"
    
def create_turn_map(output_filepath: str):
    """Create turn map (LRLRRL..) based on arm turns."""
    num_of_ys = sum(shape_of_rows)
    
    df = pd.read_csv(output_filepath)
    df.head()
    
    print(df)
    LR = [[] for j in range(num_rows)]

    for row in range(num_rows):
        num_cols = shape_of_rows[row]
        for col in range(num_cols):
            keep_ = None

            all_in_col = ""
            for z in range(0, int(len(df) / num_of_ys) - len(df) % num_of_ys - 1):
                y_count = row * num_cols + col
                indic = [y_count + z * num_of_ys,
                         y_count + z * num_of_ys + num_of_ys]

                prev = convert_to_quadrant(df['pos_x'][indic[0]],
                                           df['pos_y'][indic[0]],
                                           row, col)

                curr = convert_to_quadrant(df['pos_x'][indic[1]],
                                           df['pos_y'][indic[1]],
                                           row, col)

                if prev is not curr:
                    if prev is None and keep_ is not curr and keep_ is not None:
                        all_in_col += turn_l_r(keep_, curr)

                    if curr is None:
                        keep_ = prev

                    if prev is not None and curr is not None:
                        all_in_col += turn_l_r(prev, curr)
                        
                
            LR[row].append(all_in_col)
            all_in_col = ""
            
    return LR

for row, col in generate_row_col(shape_of_rows):
    cv2.circle(mode_noblur_img, cell_centers[row][col], 2, (0, 0, 0), 2, cv2.LINE_4)
    cell_count = row * shape_of_rows[row] + col

    for point in cell_contours[cell_count]:        
        cv2.putText(mode_noblur_img, str(convert_to_quadrant(point[0], point[1], row, col)), point, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        

turn_map = create_turn_map(data_fp)

for row in range(num_rows):
    num_cols = shape_of_rows[row]
    for col in range(num_cols):
        sets_of_four = match(turn_map[row][col])
        percent = count(sets_of_four)
        print(turn_map[row][col])
        print(percent)       
        #v.indiv_fish_plot(percent)
        v.indiv_bar_graph(percent, data_fp[:-18]+"_"+str(row)+"_"+str(col)+".png", 0)
"""
counter = 0

num_rows = len(shape_of_rows)

keep_all = [[None for i in range(shape_of_rows[j])] for j in range(num_rows)]

count_pr = [[0 for i in range(shape_of_rows[j])] for j in range(num_rows)]
show_pr = [["" for i in range(shape_of_rows[j])] for j in range(num_rows)]

count_n = [[0 for i in range(shape_of_rows[j])] for j in range(num_rows)]
show_n = [["" for i in range(shape_of_rows[j])] for j in range(num_rows)]

cont, curr_img = vidcap.read()

while cont:
    cont, curr_img = vidcap.read()

    num_of_ys = sum(shape_of_rows)

    df = pd.read_csv(data_fp)
    df.head()

    for row in range(num_rows):
        num_cols = shape_of_rows[row]
        for col in range(num_cols):
            y_count = row * num_cols + col

            indic = [y_count + counter * num_of_ys,
                     y_count + counter * num_of_ys + num_of_ys]

            prev_x, prev_y = df['pos_x'][indic[0]], df['pos_y'][indic[0]]
            curr_x, curr_y = df['pos_x'][indic[1]], df['pos_y'][indic[1]]

            prev = convert_to_quadrant(prev_x, prev_y, row, col)
            curr = convert_to_quadrant(curr_x, curr_y, row, col)

            if prev != curr:
                if (prev == None and keep_all[row][col] != curr and keep_all[row][col] != None):
                    #cv2.putText(curr_img, tetr.turn_l_r(keep_all[row][col], curr), (curr_x, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 5,
                    #           (0, 0, 0), 2, cv2.LINE_AA)
                    count_pr[row][col] = 200
                    count_n[row][col] = 0
                    show_pr[row][col] = turn_l_r(keep_all[row][col], curr)

                if curr == None:
                    keep_all[row][col] = prev

                if (prev != None and curr != None):
                    #cv2.putText(curr_img, tetr.turn_l_r(prev, curr), (curr_x, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 5,
                    #           (0, 0, 0), 2, cv2.LINE_AA)
                    count_n[row][col] = 200
                    count_pr[row][col] = 0
                    show_n[row][col] = turn_l_r(prev, curr)
            
            cv2.putText(curr_img, str(row) + "," + str(col), (cell_centers[row][col][0] - 50, cell_centers[row][col][1]), cv2.FONT_HERSHEY_SIMPLEX, 1,
                       (255, 255, 255), 2, cv2.LINE_AA)

            
            if count_pr[row][col] > 0:
                
                cv2.putText(curr_img, show_pr[row][col][0], cell_centers[row][col], cv2.FONT_HERSHEY_SIMPLEX, 1,
                           (255, 255, 255), 2, cv2.LINE_AA)
                count_pr[row][col] -= 1


            if count_n[row][col] > 0:
                cv2.putText(curr_img, show_n[row][col][0], cell_centers[row][col], cv2.FONT_HERSHEY_SIMPLEX, 1,
                           (255, 255, 255), 2, cv2.LINE_AA)
                count_n[row][col] -= 1

            cv2.putText(curr_img, str(curr), (curr_x, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                       (255, 255, 255), 2, cv2.LINE_AA)

    #result.write(curr_img)
    
    cv2.imshow("curr", curr_img)

    counter += 1

    if cv2.waitKey(int(1000 * (1 / vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))) & 0xFF == ord('q'):
        break

"""
vidcap.release()
