""""""
import os
import sys

import cv2

from visualization.helpers.roi_manip import convert_to_contours, get_contour_mask
from visualization.helpers.generate_row_col import generate_row_col
from visualization.arm_analysis import ArmAnalysis
from visualization.tetragram_analysis import TetragramAnalysis
from visualization.visualization import Visualization
from visualization.helpers.file_manip import find_all_files

import numpy as np
import pandas as pd

all_ages = {}
age_list = ["6dpf", "10dpf", "15dpf", "21dpf", "27dpf", "28dpf", "29dpf"]

v = Visualization(
    ["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"], [
        "LLLL", "RRRR", "LLLR", "RRRL", "LLRR", "RRLL", "LRRR", "RLLL", "RLLR", "LRRL", "RRLR", "LLRL", "LRLR", "RLRL",
        "LRLL", "RLRR"], 4, age_list, "viridis")

percents = {}

ages_enum = range(0, len(age_list))

#fp = sys.argv[1]
#files = find_all_files(fp, extension=".csv", exclude=["save", "2run", "3run", "4run"])
files = ["/home/chamomile/Thyme_lab/fc2_save_2025-08-27-093554-0000post-processed.csv"]
df = []
#, "15dpf", "21dpf", "27dpf", "28dpf", "29dpf"]
age_dict = {age:[0 for l in range(len(v.labels))] for age in age_list}
num_of_samples = {age:0 for age in age_list}

for data_fp in files:
#    try:
    print("DATAFP", data_fp)
    fn = data_fp[:-4]
    save_fp = data_fp[:-18] + "_save_fixed.csv"
    arm_save_fp = data_fp[:-18] + "_arm_save_fixed.csv"

    posns_save_fp = data_fp[:-18] + "post-processed.csv"

    cell_fp = data_fp[:-18] + ".cells"
    movie_fp = data_fp[:-18] + ".mp4"
    mode_fp = data_fp[:-18] + "-mode.png"

    #age = None
    #for a in age_list:
    #    if a in data_fp:
    #        age = a
    age = "6dpf"
    print(os.path.isfile(save_fp), age)
    if os.path.isfile(save_fp) and age is not None:
        # all of this is for analyzing data and getting arm and tetragram data
        cell_contours, cell_centers, shape_of_rows = convert_to_contours(cell_fp)

        SAME_DIR = True
        HORIZONTAL = True

        NUM_ROWS = len(cell_centers)

        arm_analysis = ArmAnalysis(cell_contours, cell_centers, shape_of_rows)

        print("calculating turn map")

        #curr_img = cv2.imread(mode_fp)
        vidcap = cv2.VideoCapture(movie_fp)
        cont, curr_img = vidcap.read()
        print(curr_img)

        # for row in arm_analysis.triangles:
        #    for triangle in row:
        #        for point in triangle:
        #             cv2.circle(curr_img, point, 2, (0, 0, 0), 2, cv2.LINE_4)

        """
        for row, row_cell_center in enumerate(cell_centers):
            for col, cell_center in enumerate(row_cell_center):
                print(cell_center)
                num = arm_analysis.convert_to_arm(cell_center[0], cell_center[1], row, col)
                #cv2.circle(curr_img, cell_center, 2, (255, 0, 0), 2, cv2.LINE_4)
                #cv2.putText(curr_img, str(num), cell_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(curr_img, f"{row}, {col}", cell_center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

                factor = 80

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
        """
        #cv2.imshow('f',curr_img)
        #cv2.waitKey(0)


        #cont, curr_img = vidcap.read()

        df = pd.read_csv(arm_save_fp)
        df.head()
        row, col = 1, 1
        ycount = row * shape_of_rows[row] + col
        arms_ = np.array(df.loc[(df['row'] == row) & (df['col'] == col), 'arm'])

        #f_df = pd.read_csv(arm_save_fixed_fp)
        #f_df.head()
        #f_arms_ = np.array(df.loc[(df['row'] == row) & (df['col'] == col), 'arm'])


        n_df = pd.read_csv(save_fp)
        n_df.head()
        turns_ = np.array(n_df.loc[(n_df['row'] == row) & (
                n_df['col'] == col), 'turn'])
        frames_ = np.array(n_df.loc[(n_df['row'] == row) & (
                n_df['col'] == col), 'frame'])

        pos_df = pd.read_csv(posns_save_fp)
        pos_df.head()
        posns = pos_df.loc[(pos_df['row'] == row) & (
                pos_df['col'] == col)]
        xposns = np.array(posns['pos_x'])
        yposns = np.array(posns['pos_y'])

        frame_count = 0
        c = 0

        next_frame = frames_[c]
        turn = ""
        prev_fixed_arm = ""
        prev_wrong_arm = ""
        l = ""

        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))

        mask = get_contour_mask([cell_contours[ycount]], frame_width, frame_height)
        reverse_mask = cv2.bitwise_not(mask)

        result = cv2.VideoWriter('turn-strat.avi',
                                 cv2.VideoWriter_fourcc(*'MJPG'),
                                 120, (frame_width, frame_height))

        while cont:
            cont, curr_img = vidcap.read()
            #cv2.circle(curr_img, (xposns[frame_count], yposns[frame_count]), 2, (255, 0, 0), 2, cv2.LINE_4)


            cv2.putText(curr_img, f"{arms_[frame_count]}", (xposns[frame_count], yposns[frame_count]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            if next_frame == frame_count:
                turn = str(turns_[c])
                l += turn

                c += 1
                next_frame = frames_[c]
                show_turn_count = 0

            if turn != "":
                cv2.putText(curr_img, turn, cell_centers[row][col], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

                if show_turn_count > 20:
                    turn = ""

                show_turn_count += 1

            #masked_mode_noblur_img = cv2.bitwise_and(
            #    curr_img, curr_img, mask=mask)


            #masked_mode_noblur_img = cv2.bitwise_xand(
            #    curr_img, curr_img, mask=reverse_mask)
            curr_img[mask == 0] = 255

            cv2.putText(curr_img, l, (cell_centers[row][col][0]+200, cell_centers[row][col][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            fixed_arm = arm_analysis.convert_to_arm(xposns[frame_count], yposns[frame_count], row, col)
            #if fixed_arm != arms_[frame_count] and not (fixed_arm == None and np.isnan(arms_[frame_count])):
            #    print(fixed_arm, arms_[frame_count])
#            if fixed_arm != prev_fixed_arm:
#                print("correct", fixed_arm, prev_fixed_arm)
#            if arms_[frame_count] != prev_wrong_arm and not (str(arms_[frame_count]) == 'nan' and str(prev_wrong_arm) == 'nan'):
#                print('wrong', arms_[frame_count], prev_wrong_arm)
#            prev_wrong_arm = arms_[frame_count]
#            prev_fixed_arm = fixed_arm

            #print(arm_analysis.arms)
#            for arm in arm_analysis.arms:
            #for row, col in generate_row_col(arm_analysis.shape_of_rows):
            #    arm = arm_analysis.arms[row][col]
            #    for point in arm:
            #        cv2.drawContours(curr_img, [np.array(point)], -1, (0,255,0), 3)
            #for point in arm:
            #    cv2.circle(curr_img, point, 2, (255, 0, 0), 2, cv2.LINE_4)

            result.write(curr_img)
            frame_count += 1

        # we start with tetragrams here
        #tetr = TetragramAnalysis(data_fp, v.labels, shape_of_rows, arm_analysis)

        # turn map contains the LRLRLLR pattern, in an array accessed by doing arr[row][col] to get data per fish
        #turn_map = tetr.turn_map

        #print(turn_map)
        #for row, col in generate_row_col(shape_of_rows):
            #print("calculating sets of four")
        #    sets_of_four = tetr.match(turn_map[row][col], v.NUMBER_OF_DIVISIONS)
            #print("calculating percent")
        #    percent = tetr.count(sets_of_four)

        #    age_dict[age] += percent
        #    num_of_samples[age] += 1

        #    NUM_OF_TETRAGRAMS = len(sets_of_four)
            #print(turn_map[row][col])
            #print(percent)
            # v.indiv_fish_plot(percent)

            #v.indiv_bar_graph(percent, data_fp[:-18] + "_" + str(row) + "_" + str(col) + ".png", row, col,
            #                  num_of_tetragrams=NUM_OF_TETRAGRAMS)
            # df.append([percent[6], row, col, num_of_tetragrams, fn])

        #v.indiv_bar_graph(age_dict[age]/num_of_ys, f"{data_fp[:-18]}_{age}.png", row, col, num_of_tetragrams=NUM_OF_TETRAGRAMS)
    else:
        print(f"{data_fp} is missing")


#for age in age_dict:
#    print(f"{data_fp[:-18]}_{age}.png")
#    age_dict[age] = age_dict[age] / num_of_samples[age]
#    v.paired_tetragram(age_dict[age], age, f"{fp}{age}_paired_tetragram.png")

"""
shape_dict = {shape:[0 for l in range(len(v.labels))] for shape in ["3_3", "3_5", "2_3"]}
shape_num_of_samples = {shape:0 for shape in ["3_3", "3_5", "2_3"]}

for age in age_dict:
    print(age)
    if age in ["21dpf"]:
        shape = "3_3"
    elif age in ["6dpf", "10dpf", "15dpf"]:
        shape = "3_5"
    elif age in ["27dpf", "28dpf", "29dpf"]:
        shape = "2_3"
    print(shape)
    shape_dict[shape] += age_dict[age]
    #print(sha)
    shape_dict[shape] = np.array(shape_dict[shape])
    shape_num_of_samples[shape] += num_of_samples[age]

for shape in shape_dict:
    print(shape_dict[shape], shape_num_of_samples[shape])
    shape_dict[shape] = shape_dict[shape] / shape_num_of_samples[shape]
print(f"{fp}overall_paired_tetragram.png")
v.paired_tetragram_bar_percent(shape_dict, shape_num_of_samples, f"{fp}overall_paired_tetragram.png")
#    except Exception as e:
#        print(e)
"""
# df = pd.DataFrame(np.matrix(df), columns=['row', 'col', 'arm', 'frame'])
# df.to_csv("all-fish.csv", sep=',')

# checking videos

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
# vidcap.release()
