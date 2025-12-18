""""""
import sys

import pandas as pd

from visualization.helpers.roi_manip import convert_to_contours, get_contour_mask
from visualization.arm_analysis import ArmAnalysis
from visualization.tetragram_analysis import TetragramAnalysis
from visualization.visualization import Visualization

age_list = ["6dpf", "10dpf", "15dpf", "21dpf", "27dpf", "28dpf", "29dpf"]

v = Visualization(
    ["LLLL, RRRR", "LLLR, RRRL", "LLRR, RRLL", "LRRR, RLLL", "LRRL, RLLR", "LLRL, RRLR", "LRLR, RLRL", "LRLL, RLRR"], [
        "LLLL", "RRRR", "LLLR", "RRRL", "LLRR", "RRLL", "LRRR", "RLLL", "RLLR", "LRRL", "RRLR", "LLRL", "LRLR", "RLRL",
        "LRLL", "RLRR"], 4, age_list, "viridis")

data_fp = sys.argv[1]
header = data_fp.split(".")[0]

cell_fp = f"{header[:-len('post-processed')]}.cells"
arm_save_fp = f"{header[:-len('post-processed')]}_arm_save.csv"
save_fp =  f"{header[:-len('post-processed')]}_save.csv"
cell_contours, cell_centers, shape_of_rows = convert_to_contours(cell_fp)
arm_analysis = ArmAnalysis(cell_contours, cell_centers, shape_of_rows)

df = pd.read_csv(arm_save_fp)
df.head()

tetr = TetragramAnalysis(df, v.labels, shape_of_rows, arm_analysis, arm_save_fp, save_fp)
