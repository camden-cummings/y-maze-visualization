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

        self.arms = self.find_all_arms(self.triangles, self.cell_direction)

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

    def point_in_arr(self, arr, pt):
        for arr_pt in arr:
            print(arr_pt, pt)
            if all(pt == arr_pt):
                return True
        else:
            return False

    def find_all_arms(self, triangles, cell_directions): # TODO: do this as TSP instead
        arms = [[[] for col in range(self.shape_of_rows[row])] for row in range(len(self.shape_of_rows))]
        for row in range(len(self.shape_of_rows)):
            for col in range(self.shape_of_rows[row]):
                ycount = row * self.shape_of_rows[row] + col

                cell_dir = cell_directions[row][col]
                print(cell_dir)
                tri = triangles[row][col]
                center = self.y_centers[row][col]
                all_pts = self.y_contours[ycount]

                if cell_dir == 0: # 2 arms U
                    down = sorted([point for point in all_pts if point[1] > center[1] and point[0] < center[0]], key=lambda z: z[1])
                    down.extend(sorted([point for point in all_pts if point[1] > center[1] and point[0] > center[0]], key=lambda z: z[1], reverse=True))

                    right = []

                    for point in tri:
                        if point[0] > center[0] and point[1] > center[1]:
                            right.append(np.array(point))

                    for point in tri:
                        if point[1] < center[1]:
                            right.append(np.array(point))

                    right.extend(sorted([point for point in all_pts if point[0] > center[0] and point[1] < center[1]], key=lambda z: z[1]))

                    left = []
                    for point in tri:
                        if point[0] < center[0] and point[1] > center[1]:
                            left.append(np.array(point))

                    for point in tri:
                        if point[1] < center[1]:
                            left.append(np.array(point))

                    left.extend(sorted([point for point in all_pts if point[0] < center[0] and point[1] < center[1] and not self.point_in_arr(left, point)], key=lambda z: z[1]))

                    arms[row][col] = Polygon(down), Polygon(right), Polygon(left)

                elif cell_dir == 1: # 2 arms
                    up = sorted([point for point in all_pts if point[1] < center[1] and point[0] < center[0]], key=lambda z: z[1])
                    up.extend(sorted([point for point in all_pts if point[1] < center[1] and point[0] > center[0]], key=lambda z: z[1], reverse=True))

                    right = []
                    for point in tri:
                        if point[1] > center[1]:
                            right.append(np.array(point))

                    for point in tri:
                        if point[0] < center[0] and point[1] < center[1]:
                            right.append(np.array(point))

                    right.extend(sorted([point for point in all_pts if point[0] < center[0] and point[1] > center[1] and not self.point_in_arr(right, point)], key=lambda z:z[1]))

                    left = []
                    for point in tri:
                        if point[1] > center[1]:
                            left.append(np.array(point))

                    for point in tri:
                        if point[0] > center[0] and point[1] < center[1]:
                            left.append(np.array(point))

                    left.extend(sorted([point for point in all_pts if point[0] > center[0] and point[1] > center[1]], key=lambda z:z[1]))

                    arms[row][col] = Polygon(up), Polygon(right), Polygon(left)

                elif cell_dir == 2:  # 2 arms R
                    left = sorted([point for point in all_pts if point[0] < center[0] and point[1] < center[1]], key=lambda z: z[0])
                    left.extend(sorted([point for point in all_pts if point[0] < center[0] and point[1] > center[1]], key=lambda z:z[0], reverse=True))

                    up = []
                    for point in tri:
                        if point[0] > center[0]:
                            up.append(np.array(point))
                    for point in tri:
                        if point[0] < center[0] and point[1] < center[1]:
                            up.append(np.array(point))

                    up.extend(sorted([point for point in all_pts if point[0] > center[0] and point[1] < center[1] and not self.point_in_arr(up, point)], key=lambda z: z[0]))

                    below = []
                    for point in tri:
                        if point[0] > center[0]:
                            below.append(np.array(point))
                    for point in tri:
                        if point[0] < center[0] and point[1] > center[1]:
                            below.append(np.array(point))

                    below.extend(sorted([point for point in all_pts if point[0] > center[0] and point[1] > center[1] and not self.point_in_arr(below, point)], key=lambda z: z[0]))

                    arms[row][col] = Polygon(left), Polygon(up), Polygon(below)
                elif cell_dir == 3: # 2 arms L
                    pass
        return arms

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

        cell_dir = self.cell_direction[row][col]
        if cell_dir == 0: #U
            down, right, left = self.arms[row][col]
            if pt.within(down):
                return 1
            elif pt.within(right):
                return 0
            elif pt.within(left):
                return 2
        elif cell_dir == 1: #D
            up, right, left = self.arms[row][col]
            if pt.within(up):
                return 2
            elif pt.within(right):
                return 0
            elif pt.within(left):
                return 1
        elif cell_dir == 2: #R
            left, up, below = self.arms[row][col]
            if pt.within(left):
                return 2
            elif pt.within(up):
                return 0
            elif pt.within(below):
                return 1
            else:
                return -1
        elif cell_dir == 3: #L
            if pos_x - self.y_centers[row][col][0] > 0:  # right side of y
                return 0
            elif pos_y - self.y_centers[row][col][1] > 0:  # top
                return 1
            else:
                return 2

        return None