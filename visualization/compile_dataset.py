# Make this for each physical set of Y maze's ran (like 1 per 12)
import pandas as pd
import numpy as np

from .helpers.generate_row_col import generate_row_col
from .helpers.file_manip import find_all_files
from .helpers.big_vs_small import read_in_sizes
from .tetragram_analysis import TetragramAnalysis
from .visualization import Visualization

labels = ["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"]

## HELPERS
def make_df_into_int_arr(df):
    return np.array(list(df)[1:], np.uint8)

def get_shape_of_rows_from_csv(df):
    """
    Analyzing is easier if you know how many rows and cols there are, this function gets that from a
    dataframe (rather than having to load the cells file or elsewise). This function is expecting at least
    one cell in every row.
    """
    shape_of_rows = []
    for i in range(int(np.max(make_df_into_int_arr(df['row']))) + 1):
        trim_df = df.loc[df['row'] == i, 'col']

        if len(trim_df) == 0:
            shape_of_rows.append(0)
            # raise Exception("Not enough information; there are not cells in every row.")
        else:
            shape_of_rows.append(int(np.max(make_df_into_int_arr(trim_df))) + 1)

    return shape_of_rows

def sort_into_shape_of_rows_type(shape_of_rows, shape_of_rows_std):
    """"""
    stringified_shape_of_rows = "_".join([str(i) for i in shape_of_rows])

    if not stringified_shape_of_rows in shape_of_rows_std:
        for s in shape_of_rows_std:
            if sum([int(i) for i in s.split("_")]) - sum(shape_of_rows) > 0:
                stringified_shape_of_rows = s


    return stringified_shape_of_rows

def make_global_dict(shape_of_rows, start_of_numbering):
    """
    Iterates through shape of rows giving each applicable row & col value - example usecase below in make_genotypes_dict_by_row.
    """
    return {f'{row}_{col}': f'Fish{start_of_numbering + row * shape_of_rows[row] + col}' for row, col in
            generate_row_col(shape_of_rows)}

def get_arm_stats(df, habitarm):
    n = np.array(df['arm'])

    tot = len(n)

    habitarm_perc = 100*len(n[n == habitarm])/tot
    nan_percent = 100*len(n[np.isnan(n)])/tot

    return [habitarm_perc, nan_percent]


def get_habituation_arm_percent_from_csv(alldf, fps, bin_size=600, habitarm=0):
    tot_habitarm_perc, tot_nan_percent = get_arm_stats(alldf, habitarm)

    df = pd.DataFrame(alldf)

    df['time_sec'] = df['frame'] / fps
    df['time_bin'] = (df['time_sec'] // bin_size).astype(int)

    binned_percs = [[] for i in range(2)]

    for time_bin, group in df.groupby(['time_bin'], sort=False):
        habitarm_perc, nan_percent = get_arm_stats(group, habitarm)
        binned_percs[0].append(habitarm_perc)
        binned_percs[1].append(nan_percent)

    return tot_habitarm_perc, tot_nan_percent, binned_percs

def get_age(fp, included_age_list):
    for a in included_age_list:
        if a in fp:
            age = a
            break
    else:
        age = ""

    return age

def load_turn_csv(fn, shape_of_rows_std):
    df = pd.read_csv(fn)
    print(fn, df.head())
    shape_of_rows = get_shape_of_rows_from_csv(df)
    stringified_shape_of_rows = sort_into_shape_of_rows_type(shape_of_rows, shape_of_rows_std)

    return df, shape_of_rows, stringified_shape_of_rows

def load_arm_csv(fp):
    if "jackie" in fp:
        arm_df = pd.read_csv(f'{fp[:-len("save.csv")]}arm_save.csv')
    else:
        s = fp.split("_save")
        arm_df = pd.read_csv(f'{s[0]}_arm_save{s[1]}')

    arm_df['frame'].astype(np.int64)

    return arm_df

def get_tetr_alternation(tetragrams):
    # Count alternating tetragrams (LRLR or RLRL)
    alternating = [tg for tg in tetragrams if tg in ['LRLR', 'RLRL']]
    total_tetragrams = len(tetragrams)

    # Calculate the percentage of alternating tetragrams
    alt_percent = (len(alternating) / total_tetragrams) * 100 if total_tetragrams > 0 else 0
    return alt_percent, total_tetragrams

def compile_dataset(dataset_fns, fps, included_age_list, shape_of_rows_std, size_dict=None, velocity_dict=None, BIN_SIZE=600):
    age_totals = {age: 0 for age in included_age_list}

    results = []
    start_of_numbering = 0
    for fp, age in dataset_fns.items():
        just_the_fn = fp.split("/")[-1].split("m")[0]
        if (size_dict is None or just_the_fn in size_dict.keys()) or (velocity_dict is None or just_the_fn in velocity_dict.keys()):
            turn_df, shape_of_rows, stringified_shape_of_rows = load_turn_csv(fp, shape_of_rows_std)
            frames = turn_df['frame'].astype(np.int64)
            turn_df['time_sec'] = turn_df['frame'] / fps
            turn_df['time_bin'] = (turn_df['time_sec'] // BIN_SIZE).astype(int)

            time_sec = frames / fps
            time_bin_per_turn = (time_sec // BIN_SIZE).astype(int)
            time_bins = time_bin_per_turn.unique().tolist()

            arm_df = load_arm_csv(fp)
            num_of_ys = sum(shape_of_rows)

            for row, col in generate_row_col(shape_of_rows):
                specfish_arms = arm_df.loc[(arm_df['row'] == row) & (arm_df['col'] == col)]
                specfish_turns = turn_df.loc[(turn_df['row'] == row) & (turn_df['col'] == col)]

                habitarm_perc, nan_percent, binned_percs = get_habituation_arm_percent_from_csv(specfish_arms, fps)

                global_id = f'Fish{start_of_numbering + row * shape_of_rows[row] + col}'
                genotype = age

                if size_dict:
                    size = size_dict[just_the_fn][row][col]
                if velocity_dict:
                    velocity = velocity_dict[just_the_fn][row][col]

                for time_bin in time_bins:
                    habitarm = binned_percs[0][time_bin]
                    nanarm = binned_percs[1][time_bin]
                    group = specfish_turns[specfish_turns['time_bin'] == time_bin]

                    if len(group) == 0:
                        alt_percent = 0
                        total_tetragrams = 0
                    else:
                        directions = group['turn'].tolist()  # Get the direction of turns
                        tetragrams = TetragramAnalysis.match(directions)
                        alt_percent, total_tetragrams = get_tetr_alternation(tetragrams)

                    result_dict = {
                        'fp': fp,
                        'row': row,
                        'col': col,
                        'global_id': global_id,
                        'time_bin': time_bin,
                        'alternation_percent': alt_percent,
                        'total_tetragrams': total_tetragrams,
                        'genotype': genotype,
                        'shape_of_rows': stringified_shape_of_rows,
                        'habitarm_binned': habitarm,
                        'nanarm_binned': nanarm

                    }
                    if size_dict:
                        result_dict.update({'size': size})

                    if velocity_dict:
                        result_dict.update({'velocity': velocity})

                    results.append(result_dict)

            start_of_numbering += num_of_ys
            age_totals[age] += num_of_ys

    df_bin_combined = pd.DataFrame(results)

    return df_bin_combined, age_totals


if __name__ == "__main__":
    #age_list = ["21dpf"]
    age_list = ["6dpf", "10dpf", "15dpf", "16dpf", "17dpf", "18dpf", "19dpf", "21dpf", "22dpf", "24dpf", "27dpf",
                "28dpf", "29dpf"]
    #age_list = ["10dpf", "17dpf", "18dpf", "19dpf", "21dpf", "22dpf", "24dpf"]
    #age_list = ["unsuredpf", "6dpf"]

    print(Visualization.defn_colours(age_list, 'viridis'))

    shape_of_rows_ = ['5_5_5', '4_4_4', '3_3_3', '3_3']

    #    dataset1_fns = find_all_files("/home/chamomile/Thyme_lab/data/jackie/unknowndpf", ext="csv", exclude=["arm_save_fixed"])

    dataset1_fns = find_all_files("/home/chamomile/Thyme_lab/data/jackie/", ext="csv", exclude=["arm_save"])

    age_dict = dict()
    for fp in dataset1_fns:
        age = get_age(fp, age_list)

        if len(age) > 0:
            age_dict[fp] = age

    sorted_age_dict = dict(sorted(age_dict.items(), key=lambda age: int(age[1].strip('dpf'))))
    d = read_in_sizes('comparecorrect/ymaze_age_size_jackie')
    dataset1, age_totals1 = compile_dataset(sorted_age_dict, d,30, age_list, shape_of_rows_)
    print(dataset1)

    names = dataset1['global_id'].unique().tolist()
    print(names)

    count = 0
    for n in names:
        m = np.max(dataset1.loc[dataset1['global_id'] == n, 'time_bin']) + 1
        count += m
        print(n, m, count)

    #variable_over_time(dataset1, "0s included", 'habitarm_binned')
    #variable_over_time(dataset1, "0s included", 'alternation_percent')
