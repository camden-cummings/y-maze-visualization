from .roi_manip import convert_to_contours, get_contour_mask
import pandas as pd

def read_file(f, frame_width, frame_height):
    header = f.split(".")[0][:-34]
    df = pd.read_csv(f)
    df.head()
    cell_fp = header + ".cells"

    cell_contours, cell_centers, shape_of_rows = convert_to_contours(cell_fp)

    mask = get_contour_mask(cell_contours, frame_width, frame_height)

    return header, df, cell_contours, cell_centers, shape_of_rows, mask