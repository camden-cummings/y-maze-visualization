import os
from collections import Counter

import numpy as np
import pandas as pd

from visualization.visualization.helpers.file_manip import find_all_files
from visualization.visualization import Visualization

filepath = "/home/chamomile/Thyme-lab/data/vids/brandon-data/reorg_data"

all_ages = {}
age_list = []

v = Visualization(["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"],  [
                  "LLLL", "RRRR", "LLLR", "RRRL", "LLRR", "RRLL", "LRRR", "RLLL", "RLLR", "LRRL", "RRLR", "LLRL", "LRLR", "RLRL", "LRLL", "RLRR"], 4, age_list, "viridis")

percents = {}

ages_enum = range(0, len(age_list))

files = find_all_files(filepath, extension=".csv")

df = []

def match(turn_map_indiv, number_of_divisions):
    """
    Pair set of movements into sets of number_of_divisions, i.e. if number_of_divisions is
    3, and LRLLRL is the string, will produce (LRL, RLL, LLR, LRL).
    """

    grouped = []

    for i in range(0, len(turn_map_indiv) - (number_of_divisions - 1)):
        grouped.append(turn_map_indiv[i:i + number_of_divisions])

    return grouped

def count(sets_of_four, labels):
    """Count tetragrams and create percentage of each kind of tetragram."""
    counter = Counter(sets_of_four)
    combin_counter = {l: 0 for l in labels}

    for l in labels:
        for val in counter.keys():
            if val in l:
                combin_counter[l] += counter[val]

    percent = 100 * np.array(list(combin_counter.values())
                             ) / sum(combin_counter.values())

    return percent

SHAPE_OF_ROWS = [4, 4, 4]
for data_fp in files:
    try:        
        if os.path.isfile(data_fp):
            df = pd.read_csv(data_fp)
            df.head()
            
            turn_map = [[] for i in range(len(SHAPE_OF_ROWS))]
            
            num_rows = len(SHAPE_OF_ROWS)
            

            for row in range(num_rows):
                num_cols = SHAPE_OF_ROWS[row]
                for col in range(num_cols):
                    all_LR = ""

                    for turn in df.loc[(df['row'] == row) & (df['col'] == col), 'turn']:
                        all_LR += turn
                    
                    turn_map[row].append(all_LR)
            
            # turn map contains the LRLRLLR pattern, in an array accessed by doing arr[row][col] to get data per fish
            for row in range(num_rows):
                num_cols = SHAPE_OF_ROWS[row]
                for col in range(num_cols):
                    print("calculating sets of four")
                    sets_of_four = match(turn_map[row][col], v.NUMBER_OF_DIVISIONS)
                    print("calculating percent")
                    percent = count(sets_of_four, v.labels)
                    
                    num_of_tetragrams = len(sets_of_four)
                    print(percent)       

                    v.indiv_bar_graph(percent, data_fp[:-18]+"_"+str(row)+"_"+str(col)+".png", row, col, num_of_tetragrams=num_of_tetragrams)
            
        else:
            print(f"{data_fp} is missing")
    
    except Exception as e:
        print(e)
        