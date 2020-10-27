import csv
import numpy as np
import colormath
import statistics
import gensim
import random
import math
import gensim.downloader as api
import pandas as pd
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

# read CSV into dataframe

# process the glasgow norms excel spreadsheet into pandas dataframe
df = pd.read_csv(r'gibson-et-al-RGB-conversions-munsell-sorted-V1.csv')
sorted_munsell = df['munsell'].to_numpy()
sorted_rgb = df['rgb'].to_list()

# format for drawing function
for i, val in enumerate(sorted_rgb):
    # read string as tuple
    c = eval(val)
    # convert to [0,1] scaled rgb values
    c = (float(c[0])/255, float(c[1])/255, float(c[2])/255)
    sorted_rgb[i] = c

#---------------------------------------------------------------------------------

# plot swatches
width= 10
height= 8

fig = plt.figure(figsize=(width, height))
ax = fig.add_subplot(111)

ratio = 1.0 / 1
count = math.ceil(math.sqrt(len(sorted_munsell)))
x_count = count * ratio
y_count = count / ratio
# x_count = 10.0
# y_count = 10.0
x = 0
y = 0
w = 1 / x_count
h = 1 / y_count

for i in range(len(sorted_munsell)):
    pos = ((0.9*x / x_count), 1.12*(y / y_count))
    ax.add_patch(patches.Rectangle(pos, w, 1.12*h, color=sorted_rgb[i]))
    ax.annotate(sorted_munsell[i],xy=pos,fontsize=7)
    if y >= y_count-2:
        x += 1
        y = 0
    else:
        y += 1


plt.yticks([])
plt.xticks([])
plt.savefig('gibson-et-al-swatches-V1-munsell-sorting',bbox_inches='tight',dpi=300)
plt.show()


#---------------------------------------------------------------------------------
# NOT USED
#---------------------------------------------------------------------------------
# hsv_points = np.empty([len(rgb),3])
# for i, val in enumerate(rgb):
#     # read string as tuple
#     c = eval(val)
#     # convert to [0,1] scaled rgb values
#     c = (float(c[0])/255, float(c[1])/255, float(c[2])/255)
#     # create RGB object
#     c = sRGBColor(c[0], c[1], c[2])
#     # convert RGB to HSV for sorting
#     hsv = convert_color(c, HSVColor)
#     # get HSV values from object
#     hsv = hsv.get_value_tuple()
#     # store in array
#     hsv_points[i, 0] = hsv[0]
#     hsv_points[i, 1] = hsv[1]
#     hsv_points[i, 2] = hsv[2]
#     # sort by hue
#     hsv_inds = np.argsort(hsv_points[:, 0])
#     sorted_hsv = hsv_points[hsv_inds]
#     sorted_munsell = munsell[hsv_inds]


# # convert HSV to RGB
# sorted_rgb = np.empty([len(rgb),], dtype=object)
# string_rgb = np.empty([len(rgb),])
# for i in range(len(rgb)):
#     # create LAB object
#     hsv = HSVColor(sorted_hsv[i,0], sorted_hsv[i,1], sorted_hsv[i,2])
#     # convert HSV to RGB object
#     rgb = convert_color(hsv, sRGBColor)
#     # get RGB values from object
#     rgb = rgb.get_value_tuple()
#     # store in array

#     sorted_rgb[i] = rgb
