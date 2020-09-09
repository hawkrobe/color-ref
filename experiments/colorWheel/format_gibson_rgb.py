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
df = pd.read_csv(r'gibson-et-al-RGB-conversions.csv')
munsell = df['Munsell Code'].to_numpy()[1:-1]
rgb = df['RGB'].to_list()[1:-1]


hsv_points = np.empty([len(rgb),3])
for i, val in enumerate(rgb):
    # read string as tuple
    c = eval(val)
    # convert to [0,1] scaled rgb values
    c = (float(c[0])/255, float(c[1])/255, float(c[2])/255)
    # create RGB object
    c = sRGBColor(c[0], c[1], c[2])
    # convert RGB to HSV for sorting 
    hsv = convert_color(c, HSVColor)
    # get HSV values from object
    hsv = hsv.get_value_tuple()
    # store in array
    hsv_points[i, 0] = hsv[0]
    hsv_points[i, 1] = hsv[1]
    hsv_points[i, 2] = hsv[2]
    # sort by hue
    hsv_inds = np.argsort(hsv_points[:, 0])
    sorted_hsv = hsv_points[hsv_inds]
    sorted_munsell = munsell[hsv_inds]


# convert HSV to RGB
sorted_rgb = np.empty([len(rgb),], dtype=object)
string_rgb = np.empty([len(rgb),])
for i in range(len(rgb)):
    # create LAB object
    hsv = HSVColor(sorted_hsv[i,0], sorted_hsv[i,1], sorted_hsv[i,2])
    # convert HSV to RGB object
    rgb = convert_color(hsv, sRGBColor)
    # get RGB values from object
    rgb = rgb.get_value_tuple()
    # store in array

    sorted_rgb[i] = rgb

#---------------------------------------------------------------------------------
# make dataframe with all these columns 
df = pd.DataFrame({'Munsell':sorted_munsell, 'RGB':sorted_rgb})

formatted_rgb = []
for index, row in df.iterrows():
    formatted_rgb.append("(" + str(int(row['RGB'][0]*255)) + ", " + str(int(row['RGB'][1]*255)) + ", " + str(int(row['RGB'][2]*255)) + ")")

id = []
for index, row in df.iterrows():
    id.append(index)

#format for experiment input
df = pd.DataFrame({'id':id, 'munsell':sorted_munsell, 'rgb':formatted_rgb})

#---------------------------------------------------------------------------------
# save df as csv
#df.to_csv('gibson-et-al-RGB-conversions-sorted.csv', index=False)

# save df as csv
df.to_json('munsell-gibson.json', orient='records')

