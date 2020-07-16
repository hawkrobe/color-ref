import csv
import numpy as np
import colormath
import statistics
import gensim
import random
import math
import gensim.downloader as api
from collections import defaultdict
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
from mpl_toolkits.mplot3d import axes3d, Axes3D
from statistics import mean 
#---------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib

#---------------------------------------------------------------------------------

# STEP 1: CIELab --> HSV, sort by hue, sorted-HSV --> RGB
words = ['dog', 'mortal', 'big', 'adjective', 'religion', 'rain', 'lime', 'noun', 'angry', 'cloud', 'door', 'justice', 'berry', 'sad', 'tree', 'verb', 'existence', 'running', 'sky', 'fun', 'soaring', 'pain', 'equality', 'universe']

for index, word in enumerate(words):
    with open('%s.txt' % (word)) as fp: 
        # get CIELab values associated with word
        points = fp.readlines()
        fp.close()

    # store each point in a numpy array of dimensions num_points x LAB
    hsv_points = np.empty([len(points),3])
    for line_num, point in enumerate(points):
        point = point.split(" ")

        # create LAB object
        lab = LabColor(float(point[0]), float(point[1]), float(point[2][:-1]))
        # convert CIELab to HSV object
        hsv = convert_color(lab, HSVColor)
        # get HSV values from object
        hsv = hsv.get_value_tuple()
        # store in array
        hsv_points[line_num, 0] = hsv[0]
        hsv_points[line_num, 1] = hsv[1]
        hsv_points[line_num, 2] = hsv[2]

        # sort by hue
        sorted_hsv = hsv_points[np.argsort(hsv_points[:, 0])]

    # convert HSV to RGB
    sorted_rgb = np.empty([len(points),], dtype=object)
    for i in range(len(points)):
        # create LAB object
        hsv = HSVColor(sorted_hsv[i,0], sorted_hsv[i,1], sorted_hsv[i,2])
        # convert HSV to RGB object
        rgb = convert_color(hsv, sRGBColor)
        # get RGB values from object
        rgb = rgb.get_value_tuple()
        # store in array
        sorted_rgb[i] = rgb
    
    width= 8
    height= 8

    fig = plt.figure(figsize=(width,height))
    ax = fig.add_subplot(111)

    ratio = 1.0 / 2.8
    count = math.ceil(math.sqrt(len(points)))
    print(count)
    x_count = count * ratio
    y_count = count / ratio
    x = 0
    y = 0
    w = 1 / x_count
    h = 1 / y_count

    for i in range(len(points)):
        pos = (x / x_count, y / y_count)
        ax.add_patch(patches.Rectangle(pos, w, h, color=sorted_rgb[i]))
        #ax.annotate(c,xy=pos,fontsize=10)
        if y >= y_count-1:
            x += 1
            y = 0
        else:
            y += 1
            

    plt.yticks([])
    plt.xticks([])
    plt.savefig('%s-swatches' % (word),bbox_inches='tight',dpi=300)
    #plt.show()