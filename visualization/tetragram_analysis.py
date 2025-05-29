""""""
from collections import Counter

import numpy as np
import pandas as pd

from visualization.helpers.generate_row_col import generate_row_col

class TetragramAnalysis:
    """"""
    def __init__(self, tracked_csv_filename, labels, shape_of_rows, arm_analysis, arm_output_filepath=None, output_filepath=None):
        self.labels = labels
        self.shape_of_rows = shape_of_rows
        self.arm_analysis = arm_analysis
        self.turn_map = self.create_turn_map(tracked_csv_filename, arm_output_filepath, output_filepath)

    def create_turn_map(self, tracked_csv_filename: str, arm_output_filepath=None, output_filepath=None):
        """Create turn map (LRLRRL..) based on arm turns."""

        df = pd.read_csv(tracked_csv_filename)
        df.head()

        num_of_ys = sum(self.shape_of_rows)
        num_rows = len(self.shape_of_rows)

        turn_map = [[] for row in range(num_rows)]

        if output_filepath:
            save_df = []
        if arm_output_filepath:
            save_arm_df = []

        for row, col in generate_row_col(self.shape_of_rows):
            y_count = row * self.shape_of_rows[row] + col

            keep_ = None

            all_in_col = ""

            for z in range(0, int(len(df) / num_of_ys) - len(df) % num_of_ys - 1):
                indic = [y_count + z * num_of_ys,
                         y_count + z * num_of_ys + num_of_ys]

                prev = self.arm_analysis.convert_to_arm(df['pos_x'][indic[0]],
                                           df['pos_y'][indic[0]],
                                           row, col)
                curr = self.arm_analysis.convert_to_arm(df['pos_x'][indic[1]],
                                           df['pos_y'][indic[1]],
                                           row, col)

                if arm_output_filepath:
                    save_arm_df.append([row, col, str(prev), df['frame'][indic[1]]])

                if prev is not curr:
                    if prev is None and keep_ is not curr and keep_ is not None:
                        turn = self.turn_l_r(keep_, curr)
                        all_in_col += turn

                        if output_filepath:
                            save_df.append([row, col, turn, df['frame'][indic[1]]])

                    if curr is None:
                        keep_ = prev

                    if prev is not None and curr is not None:
                        turn = self.turn_l_r(prev, curr)
                        all_in_col += turn

                        if output_filepath:
                            save_df.append([row, col, turn, df['frame'][indic[1]]])

            turn_map[row].append(all_in_col)

        if arm_output_filepath:
            save_arm_df = pd.DataFrame(np.matrix(save_arm_df), columns=['row', 'col', 'arm', 'frame'])
            save_arm_df.to_csv(arm_output_filepath, sep=',')

        if output_filepath:
            save_df = pd.DataFrame(np.matrix(save_df), columns=['row', 'col', 'turn', 'frame'])
            save_df.to_csv(output_filepath, sep=',')

        return turn_map

    """
    @staticmethod
    def match_threes(l):
        # Pair set of movements into each arm into sets of three, i.e.
        # if there are 4 arms and 012302 is the string, will produce
        # (012, 123, 230, 302).

        
        sets_of_three = []

        for i in range(0, len(l) - 2):
            sets_of_three.append(l[i:i+3])

        return sets_of_three
    """

    def create_arm_list(self, output_filepath: str):
        """Like mice data, w/ % spontaneous alternation instead of tetragrams."""

        df = pd.read_csv(output_filepath)
        df.head()

        num_rows = len(self.shape_of_rows)
        num_of_ys = sum(self.shape_of_rows)

        arm_list = [[[] for col in range(self.shape_of_rows[row])] for row in range(num_rows)]
        just_the_hits_arm_list = [[[] for col in range(self.shape_of_rows[row])] for row in range(num_rows)]
        for row, col in generate_row_col(self.shape_of_rows):
            for z in range(0, int(len(df) / num_of_ys) - len(df) % num_of_ys - 1):
                y_count = row * self.shape_of_rows[row] + col
                indic = [y_count + z * num_of_ys,
                         y_count + z * num_of_ys + num_of_ys]

                prev = self.arm_analysis.convert_to_arm(df['pos_x'][indic[0]], df['pos_y'][indic[0]],
                                           row, col)
                curr = self.arm_analysis.convert_to_arm(df['pos_x'][indic[1]], df['pos_y'][indic[1]],
                                           row, col)

                arm_list[row][col].append(str(prev))

                if prev is not curr and prev is not None:
                    just_the_hits_arm_list[row][col].append(str(prev))

        return arm_list, just_the_hits_arm_list

    @staticmethod
    def spontaneous_alternation_percent(l):
        """Calculates the spontaneous alternation percent for a given pattern."""
        if len(l) == 0:
            return -1

        count = 0
        for i in l:
            if len(i) > len(set(i)):  # if it has multiple of the same number, count += 1
                count += 1

        return (len(l) - count) / len(l)

    def match(self, turn_map_indiv, number_of_divisions):
        """
        Pair set of movements into sets of number_of_divisions, i.e. if number_of_divisions is
        3, and LRLLRL is the string, will produce (LRL, RLL, LLR, LRL).
        """

        grouped = []

        for i in range(0, len(turn_map_indiv) - (number_of_divisions - 1)):
            grouped.append(turn_map_indiv[i:i + number_of_divisions])

        return grouped

    def match_for_row_and_col(self, turn_map, number_of_divisions):
        """Run match for each of the cells."""
        grouped = []

        num_rows = len(self.shape_of_rows)
        for row, col in generate_row_col(self.shape_of_rows):
            l = turn_map[row][col]
            grouped.extend(self.match(l, number_of_divisions))

        return grouped

    @staticmethod
    def turn_l_r(prev_arm: int, curr_arm: int) -> str:
        """Decides if moving from previous arm to current arm was turning left or turning right."""
        if (prev_arm, curr_arm) == (0, 2):
            return "L"

        elif (prev_arm, curr_arm) == (2, 0):
            return "R"

        elif prev_arm < curr_arm:
            return "R"

        else:
            return "L"

    def count(self, sets_of_four):
        """Count tetragrams and create percentage of each kind of tetragram."""
        counter = Counter(sets_of_four)
        combin_counter = {l: 0 for l in self.labels}

        for l in self.labels:
            for val in counter.keys():
                if val in l:
                    combin_counter[l] += counter[val]

        percent = 100 * np.array(list(combin_counter.values())
                                 ) / sum(combin_counter.values())

        return percent
