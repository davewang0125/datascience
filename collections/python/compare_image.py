#!/usr/bin/env python
"""Compare two aligned images of the same size.
Usage: python compare.py first-image second-image
"""

import sys

from imageio import imread
import numpy as np
from scipy.linalg import norm
from scipy import sum, average
import re
import json
class imagecompare:
    
    def __init__(self):
        pass
        
    
    def compare_image_files(self, file1, file2):
        img1 = imread(file1)
        img2 = imread(file2)
        return self.compare_images(img1, img2)

    def compare_images(self, img1, img2):
        # normalize to compensate for exposure difference, this may be unnecessary
        # consider disabling it
        img1 = self.normalize(img1)
        img2 = self.normalize(img2)
        # calculate the difference and its norms
        diff = img1 - img2  # elementwise for scipy arrays
        m_norm = np.sum(abs(diff))/img1.size  # Manhattan norm
        z_norm = norm(diff.ravel(), 0)/img1.size  # Zero norm
        # print ("Manhattan norm:", m_norm, "/ per pixel:", m_norm/img1.size)
        # print ("Zero norm:", z_norm, "/ per pixel:", z_norm*1.0/img1.size)
    
        return (m_norm, z_norm)

    def to_grayscale(self, arr):
        "If arr is a color image (3D array), convert it to grayscale (2D array)."
        if len(arr.shape) == 3:
            return average(arr, -1)  # average over the last axis (color channels)
        else:
            return arr
        
    def normalize(self, arr):
        rng = arr.max()-arr.min()
        amin = arr.min()
        return (arr-amin)*255/rng

def main():
    img1 = imread("live0.png")
    img2 = imread("live200.png")
    img = imagecompare()
    n_m, n_0 = img.compare_image_files("live0.png", "live200.png")
    print ("Manhattan norm:", n_m, "/ per pixel:", n_m/img1.size)
    print ("Zero norm:", n_0, "/ per pixel:", n_0*1.0/img1.size)
    
if __name__ == '__main__':
    main()
