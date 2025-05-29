""""""
import cv2
import numpy as np
import math

from shapely.geometry import Point, Polygon

from visualization.helpers.generate_row_col import generate_row_col

class ArmAnalysis:
    def __init__(self, y_contours, y_centers, shape_of_rows, same_dir, horizontal):
        self.y_contours = y_contours
        self.y_centers = y_centers
        self.shape_of_rows = shape_of_rows
        self.same_dir = same_dir
        self.horizontal = horizontal
        self.triangles = self.find_all_triangles()

        self.deciding_factor = self.decide_even_or_odd()

    def decide_even_or_odd(self):
        """
        Deciding if each cell is in an even row/col or an odd one.
        """
        if not self.horizontal:
            upper_half = []
            lower_half = []

            for point in self.y_contours[0]:  # DOUBLE CHECK THIS
                if abs(point[1] - self.y_centers[0][0][1]) < 50:
                    lower_half.append(point)
                    upper_half.append(point)
                elif point[1] > self.y_centers[0][0][1]:
                    lower_half.append(point)
                else:
                    upper_half.append(point)

            if cv2.contourArea(np.array(upper_half)) > cv2.contourArea(np.array(lower_half)):
                print("first Y has two arms above the center")
                return 0

            print("first Y has two arms below the center")
            return 1

        else:
            return self.decide_left_or_right(0)

    def decide_left_or_right(self, cell_num):
        """Decides if given cell in contours has two arms on the left or on the right."""
        left_half = []
        right_half = []

        num_rows = len(self.shape_of_rows)
        which_row = cell_num % (num_rows - 1)

        for point in self.y_contours[cell_num]:
            num_cols = self.shape_of_rows[which_row]

            if [point[0], point[1]] not in self.triangles[int(cell_num / num_cols)][cell_num % num_cols]:
                if point[0] < self.y_centers[int(cell_num / num_cols)][cell_num % num_cols][0]:
                    left_half.append(point)
                    # cv2.circle(mode_blur_img, point, 1, (255, 0, 0), 5, cv2.LINE_4)
                else:
                    right_half.append(point)
                    # cv2.circle(mode_blur_img, point, 1, (0, 0, 255), 5, cv2.LINE_4)

        right_half.append(self.y_centers[int(cell_num / num_cols)][cell_num % num_cols])
        left_half.append(self.y_centers[int(cell_num / num_cols)][cell_num % num_cols])

        # cv2.imshow('f',mode_blur_img)
        # cv2.waitKey(0)

        if cv2.contourArea(np.array(left_half)) > cv2.contourArea(np.array(right_half)):
            print("Y has two arms left")
            return 0
        print("Y has two arms right")
        return 1

    def find_closest_three(self, contour, center):
        all_contour_pts = []
        for c in contour:
            all_contour_pts.append([c, math.dist(c, center)])

        all_contour_pts.sort(key=lambda tup: tup[1])
        closest_three = all_contour_pts[:3]

        triangle = [[i[0][0], i[0][1]] for i in closest_three]

        return triangle

    def find_all_triangles(self):
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

        if not self.same_dir and self.horizontal:
            if row % 2 == self.deciding_factor:  # two arms on left
                if pos_x - self.y_centers[row][col][0] > 0:  # right side of y
                    return 0
                elif pos_y - self.y_centers[row][col][1] > 0:  # top
                    return 1
                else:
                    return 2

            else:  # two arms on right - Y
                if pos_x - self.y_centers[row][col][0] < 0:  # left side of y
                    return 0
                elif pos_y - self.y_centers[row][col][1] > 0:  # top
                    return 1
                else:
                    return 2
        elif not self.same_dir and not self.horizontal:
            if col % 2 == self.deciding_factor:  # two arms on top
                if pos_y - self.y_centers[row][col][1] > 0:  # top
                    return 0
                elif pos_x - self.y_centers[row][col][0] < 0:
                    return 1
                else:
                    return 2
            else:  # two arms on bottom
                # print("two arms on bottom")
                if pos_y - self.y_centers[row][col][1] < 0:  # bottom
                    return 0
                elif pos_x - self.y_centers[row][col][0] < 0:
                    return 2
                else:
                    return 1
        elif self.same_dir:  # Y
            # same direction - need to decide whether two arms to left or two arms to right
            if self.deciding_factor == 1:
                # two arms to left side of y
                if pos_x - self.y_centers[row][col][0] < 0:
                    return 2
                elif pos_y - self.y_centers[row][col][1] > 0:  # top
                    return 1
                else:
                    return 0
            elif self.deciding_factor == 0:
                # two arms to right side of y
                if pos_x - self.y_centers[row][col][0] > 0:
                    return 1
                elif pos_y - self.y_centers[row][col][1] < 0:  # bottom
                    return 0
                else:
                    return 2
        return None