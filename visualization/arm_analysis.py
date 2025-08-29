""""""
import cv2
import numpy as np
import math

from shapely.geometry import Point, Polygon

from visualization.helpers.generate_row_col import generate_row_col

class ArmAnalysis:
    def __init__(self, y_contours, y_centers, shape_of_rows):
        self.y_contours = y_contours
        self.y_centers = y_centers
        self.shape_of_rows = shape_of_rows
        self.triangles = self.find_all_triangles()

        self.cell_direction = [[[] for j in range(self.shape_of_rows[i])] for i in range(len(self.shape_of_rows))]

        for row in range(len(self.shape_of_rows)):
            for col in range(self.shape_of_rows[row]):
                ycount = row * shape_of_rows[row] + col
                self.cell_direction[row][col] = self.cell_direction_finder(ycount)

    def cell_direction_finder(self, cell_num):
        """Deciding if each cell is in an even row/col or an odd one."""
        upper_half = []
        lower_half = []
        left_half = []
        right_half = []

        for row_num in range(len(self.shape_of_rows)):
            if cell_num < sum(self.shape_of_rows[0:row_num+1]):
                which_row = row_num
                break

        for point in self.y_contours[cell_num]:
            num_cols = self.shape_of_rows[which_row]

            if [point[0], point[1]] not in self.triangles[int(cell_num / num_cols)][cell_num % num_cols]:
                if point[1] < self.y_centers[int(cell_num / num_cols)][cell_num % num_cols][1]:
                    upper_half.append(point)
                else:
                    lower_half.append(point)

        for point in self.y_contours[cell_num]:
            num_cols = self.shape_of_rows[which_row]

            if [point[0], point[1]] not in self.triangles[int(cell_num / num_cols)][cell_num % num_cols]:
                if point[0] < self.y_centers[int(cell_num / num_cols)][cell_num % num_cols][0]:
                    left_half.append(point)
                else:
                    right_half.append(point)

        center = self.y_centers[which_row][cell_num % num_cols]

        upper_half.append(center)
        lower_half.append(center)
        right_half.append(center)
        left_half.append(center)

        up_tri_area, _ = cv2.minEnclosingTriangle(np.array(upper_half))
        low_tri_area, _ = cv2.minEnclosingTriangle(np.array(lower_half))
        right_tri_area, _ = cv2.minEnclosingTriangle(np.array(right_half))
        left_tri_area, _ = cv2.minEnclosingTriangle(np.array(left_half))

        areas = [up_tri_area, low_tri_area, right_tri_area, left_tri_area]

        ind = np.argmax(areas)

        return int(ind)

    @staticmethod
    def find_closest_three(contour, center):
        """"""
        all_contour_pts = []
        for c in contour:
            all_contour_pts.append([c, math.dist(c, center)])

        all_contour_pts.sort(key=lambda tup: tup[1])
        closest_three = all_contour_pts[:3]

        triangle = [[i[0][0], i[0][1]] for i in closest_three]

        return triangle

    def find_all_triangles(self):
        """"""
        num_rows = len(self.shape_of_rows)
        triangles = [[] for r in range(num_rows)]
        for row, col in generate_row_col(self.shape_of_rows):
            y_count = row * self.shape_of_rows[row] + col

            triangle = self.find_closest_three(
                self.y_contours[y_count], self.y_centers[row][col])
            triangles[row].append(triangle)

        return triangles

    def convert_to_arm(self, pos_x: int, pos_y: int, row: int, col: int):
        """
        Spits out which arm the fish is currently in.

        Parameters
        ----------
        pos_x
            DESCRIPTION.
        pos_y
            DESCRIPTION.
        row
            DESCRIPTION.
        col
            DESCRIPTION.
        even_or_odd
            DESCRIPTION.

        Returns
        -------
        int
            DESCRIPTION.

        """
        pt = Point([pos_x, pos_y])
        poly = Polygon(self.triangles[row][col])

        if pt.within(poly):
            return None

        dir = self.cell_direction[row][col]
        if dir == 0: #U
            if pos_y - self.y_centers[row][col][1] > 0:  # top
                return 0
            elif pos_x - self.y_centers[row][col][0] < 0:
                return 1
            else:
                return 2
        elif dir == 1: #D
            if pos_y - self.y_centers[row][col][1] < 0:  # bottom
                return 0
            elif pos_x - self.y_centers[row][col][0] < 0:
                return 2
            else:
                return 1
        elif dir == 2: #R
            if pos_x - self.y_centers[row][col][0] < 0:  # left side of y
                return 0
            elif pos_y - self.y_centers[row][col][1] > 0:  # top
                return 1
            else:
                return 2
        elif dir == 3: #L
            if pos_x - self.y_centers[row][col][0] > 0:  # right side of y
                return 0
            elif pos_y - self.y_centers[row][col][1] > 0:  # top
                return 1
            else:
                return 2

        return None