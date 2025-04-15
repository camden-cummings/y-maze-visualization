#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from helpers.file_manip import find_all_files

from visualization.tetragram_analysis import TetragramAnalysis
from visualization.visualization import Visualization

from roi_manip import convert_to_contours

from cell_finder import ArmAnalysis

import os

import cv2

filepath = "/home/chamomile/Thyme-lab/data/vids/social_and_many_well/to-be-processed/march/fc2_save_2025-03-01-162813-0000.mp4"

all_ages = {}
age_list = []

v = Visualization(["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"],  [
                  "LLLL", "RRRR", "LLLR", "RRRL", "LLRR", "RRLL", "LRRR", "RLLL", "RLLR", "LRRL", "RRLR", "LLRL", "LRLR", "RLRL", "LRLL", "RLRR"], 4, age_list, "viridis")

percents = {}

ages_enum = range(0, len(age_list))

#files = find_all_files(filepath, extension=".csv")
files=["/home/chamomile/Thyme-lab/data/vids/social_and_many_well/fc2_save_2025-02-06-111321-0000pre-processed.csv"]
df = []

for data_fp in files:
    try:
        fn = data_fp[:-4]
        #save_fp = data_fp[:-18] + "_save.csv"
        #arm_save_fp = data_fp[:-18] + "_arm_save.csv"
        cell_fp = data_fp[:-17] + ".cells"
        movie_fp = data_fp[:-17] + ".mp4"
        
        if os.path.isfile(data_fp):
            # all of this is for analyzing data and getting arm and tetragram data
            cell_contours, cell_centers, shape_of_rows = convert_to_contours(cell_fp)
            
            same_dir = True
            horizontal = True
            
            num_rows = len(cell_centers)
                
            arm_analysis = ArmAnalysis(cell_contours, cell_centers, shape_of_rows, same_dir, horizontal)
            
            if same_dir:
                left_or_right = arm_analysis.decide_left_or_right(0)
                arm_analysis.deciding_factor = left_or_right
            else:
                even_or_odd = arm_analysis.decide_even_or_odd()
                arm_analysis.deciding_factor = even_or_odd
            
            print("calculating turn map")
            
            vidcap = cv2.VideoCapture(movie_fp)
            
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, 1000)

            cont, curr_img = vidcap.read()
            
            #for row in arm_analysis.triangles:
            #    for triangle in row:
            #        for point in triangle:
            #             cv2.circle(curr_img, point, 2, (0, 0, 0), 2, cv2.LINE_4)
            
            for row, row_cell_center in enumerate(cell_centers):
                for col, cell_center in enumerate(row_cell_center):
                    print(cell_center)
                    num = arm_analysis.convert_to_arm(cell_center[0], cell_center[1], row, col)
            
                    #cv2.circle(curr_img, cell_center, 2, (255, 0, 0), 2, cv2.LINE_4)
                    #cv2.putText(curr_img, str(num), cell_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(curr_img, f"{row}, {col}", cell_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    
                    factor = 80
                    if arm_analysis.deciding_factor == 0:
                        factor = factor
                    elif arm_analysis.deciding_factor == 1:
                        factor = -factor
                        
                    x=[cell_center[0]-factor, cell_center[1]-factor]
                    y=[cell_center[0]-factor, cell_center[1]+factor]
                    z=[cell_center[0]+factor, cell_center[1]]
                    
                    #xa=[cell_center[0]+150, cell_center[1]+150]
                    #ya=[cell_center[0]+150, cell_center[1]-150]
                    #za=[cell_center[0]-150, cell_center[1]]
                    cv2.putText(curr_img, str(arm_analysis.convert_to_arm(x[0], x[1], row, col)), x, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(curr_img, str(arm_analysis.convert_to_arm(y[0], y[1], row, col)), y, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(curr_img, str(arm_analysis.convert_to_arm(z[0], z[1], row, col)), z, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    
                    #cv2.putText(curr_img, str(arm_analysis.convert_to_arm(x[0], xa[1], row, col)), xa, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    #cv2.putText(curr_img, str(arm_analysis.convert_to_arm(y[0], ya[1], row, col)), ya, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    #cv2.putText(curr_img, str(arm_analysis.convert_to_arm(z[0], za[1], row, col)), za, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.circle(curr_img, x, 2, (255, 0, 0), 2, cv2.LINE_4)
                    cv2.circle(curr_img, y, 2, (255, 0, 0), 2, cv2.LINE_4)
                    cv2.circle(curr_img, z, 2, (255, 0, 0), 2, cv2.LINE_4)
            
            cv2.imshow('f',curr_img)
            cv2.waitKey(0)
            
            # we start with tetragrams here
            tetr = TetragramAnalysis(data_fp, v.labels, shape_of_rows, arm_analysis)
            
            # turn map contains the LRLRLLR pattern, in an array accessed by doing arr[row][col] to get data per fish
            turn_map = tetr.turn_map
            
            print(turn_map)
            for row in range(num_rows):
                num_cols = shape_of_rows[row]
                for col in range(num_cols):
                    print("calculating sets of four")
                    sets_of_four = tetr.match(turn_map[row][col], v.NUMBER_OF_DIVISIONS)
                    print("calculating percent")
                    percent = tetr.count(sets_of_four)
                    
                    num_of_tetragrams = len(sets_of_four)
                    print(turn_map[row][col])
                    print(percent)       
                    #v.indiv_fish_plot(percent)
                    v.indiv_bar_graph(percent, data_fp[:-18]+"_"+str(row)+"_"+str(col)+".png", row, col, num_of_tetragrams=num_of_tetragrams)
                    df.append([percent[6], row, col, num_of_tetragrams, fn])
        
        else:
            print(f"{data_fp} is missing")
    
    except Exception as e:
        print(e)
        
#df = pd.DataFrame(np.matrix(df), columns=[
#                  'LRLR RLRLR percent', 'row', 'col', 'num_of_tetragrams', 'name'])
#df.to_csv("all-fish.csv", sep=',')

#checking videos

"""
cont, curr_img = vidcap.read()

counter = 0

print("deciding factor: ", deciding_factor, arm_analysis.deciding_factor)
keep_all = [[None for i in range(shape_of_rows[j])] for j in range(num_rows)]

count_pr = [[0 for i in range(shape_of_rows[j])] for j in range(num_rows)]
show_pr = [["" for i in range(shape_of_rows[j])] for j in range(num_rows)]

count_n = [[0 for i in range(shape_of_rows[j])] for j in range(num_rows)]
show_n = [["" for i in range(shape_of_rows[j])] for j in range(num_rows)]

frame_width = int(vidcap.get(3))
frame_height = int(vidcap.get(4))

fps = vidcap.get(cv2.CAP_PROP_FPS)

result = cv2.VideoWriter(data_fp[:-18]+'_left_or_right.avi',
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         fps, (frame_width, frame_height))
    
while counter < 1500:
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

            prev = arm_analysis.convert_to_arm(prev_x, prev_y, row, col)
            curr = arm_analysis.convert_to_arm(curr_x, curr_y, row, col)

            if prev != curr:
                if (prev == None and keep_all[row][col] != curr and keep_all[row][col] != None):
                    #cv2.putText(curr_img, tetr.turn_l_r(keep_all[row][col], curr), (curr_x, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 5,
                    #           (0, 0, 0), 2, cv2.LINE_AA)
                    count_pr[row][col] = 200
                    count_n[row][col] = 0
                    show_pr[row][col] = tetr.turn_l_r(keep_all[row][col], curr)

                if curr == None:
                    keep_all[row][col] = prev

                if (prev != None and curr != None):
                    #cv2.putText(curr_img, tetr.turn_l_r(prev, curr), (curr_x, curr_y), cv2.FONT_HERSHEY_SIMPLEX, 5,
                    #           (0, 0, 0), 2, cv2.LINE_AA)
                    count_n[row][col] = 200
                    count_pr[row][col] = 0
                    show_n[row][col] = tetr.turn_l_r(prev, curr)
            
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

    result.write(curr_img)
    
    
    
    #cv2.imshow("curr", curr_img)

    counter += 1

    #if cv2.waitKey(int(1000 * (1 / vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))) & 0xFF == ord('q'):
    #    break
"""
#vidcap.release()
