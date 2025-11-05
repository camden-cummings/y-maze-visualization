#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 14:44:39 2025

@author: chamomile
"""

import pickle
import math

import numpy as np
import cv2

#TODO add auto trimmer that finds dimensions that can trim the image to to still include all of every contour

def convert_to_contours(cell_filename): 
    if isinstance(cell_filename, str):
        with open(cell_filename, 'rb') as f:
            rois = pickle.load(f)
            
#            if isinstance(rois, RoiPoly):
#                rois_dup = []
#                for roi in rois:
#                    rois_dup.append(roi.lines)
#                rois = rois_dup
    else:
        rois = cell_filename
        
    centers = []
    contours = []

    for roi in rois:
        contour = np.array(roi, dtype='int')
        contours.append(contour)
        
        cx, cy = find_centroid_of_contour(contour)
        
        for center in centers:
            if math.dist(center[0], (cx,cy)) == 0.0:
                break
        else:
            centers.append([[cx, cy], contour])
    
    centers.sort(key=lambda tup: tup[0][1])
    
    row = 0
    reorg_centers = []
    curr_row = []
    
    #sorting by row  ------------------------
    for i in range(0, len(centers)):
        if centers[i][0][1] - centers[i-1][0][1] > 40:
            row += 1
            curr_row.sort(key=lambda tup: tup[0][0])
            reorg_centers.append(curr_row.copy())
            curr_row.clear()
            
        curr_row.append(centers[i])
        
        if i == len(centers)-1:
            curr_row.sort(key=lambda tup: tup[0][0])
            reorg_centers.append(curr_row)

    num_rows = len(reorg_centers)
    # ------------------------
    #TODO if not possible try to group by vertical alignment

    cell_contours = [[] for i in range(len(centers))]
    cell_centers = [[] for j in range(num_rows)]

    shape_of_rows = []

    for row in range(num_rows):
        num_cols = len(reorg_centers[row])
        shape_of_rows.append(num_cols)
        for col in range(num_cols):
            y_count = row * num_cols + col
            
            cell_centers[row].append(reorg_centers[row][col][0])
            cell_contours[y_count] = reorg_centers[row][col][1]

    
    return cell_contours, cell_centers, shape_of_rows

def get_contour_mask(cell_contours, frame_width, frame_height):
    contour_mask = np.zeros((frame_height, frame_width, 3))

    for c in cell_contours:
        contour_mask = cv2.drawContours(contour_mask, [c],
                                        -1, (255, 255, 255), thickness=cv2.FILLED)

    contour_mask = cv2.cvtColor(
        np.array(contour_mask, dtype=np.uint8), cv2.COLOR_BGR2GRAY)

    return contour_mask

def find_centroid_of_contour(contour):
    """Given a contour, finds centroid of it."""
    M = cv2.moments(contour)

    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy
