""""""

def generate_row_col(shape_of_rows):
    for row_num, item in enumerate(shape_of_rows):
        for col_num in range(item):
            yield row_num, col_num