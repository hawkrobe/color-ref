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
#---------------------------------------------------------------------------------
# read CSV into dataframe

# process the glasgow norms excel spreadsheet into pandas dataframe
df = pd.read_csv(r'gibson-et-al-RGB-conversions.csv')
munsell = df['Munsell Code'].to_list()
rgb = df['RGB'].to_list()

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
R10 = np.array([0, 22, 44, 66, 88])
R5 = np.array([11, 33, 55, 77,])

# SORTING VERSION 1: GROUP ALL OF ONE COLOR TOGETHER REGARDLESS OF
# WHERE IT IS ON THE HUE BAND (I.E. 10R, 5R, 10R, 5R)
sorted_munsell = []
sorted_rgb = []
for val in range(11):
    color10 = R10 + val
    color5 = R5 + val
    for i in range(len(munsell)):
        if i in color10:
            sorted_munsell.append(munsell[i])
            sorted_rgb.append(rgb[i])
        if i in color5:
            sorted_munsell.append(munsell[i])
            sorted_rgb.append(rgb[i])

# # reverse values
# ordered_munsell = []
# ordered_rgb = []
# start = 0
# end = 8
# for i in range(10):
#     ordered_munsell += sorted_munsell[start+(8*i):end+(8*i)][::-1]
#     ordered_rgb += sorted_rgb[start+(8*i):end+(8*i)][::-1]

#---------------------------------------------------------------------------------
# make dataframe with all these columns
df = pd.DataFrame({'Munsell':sorted_munsell, 'RGB':sorted_rgb})

id = []
for index, row in df.iterrows():
    id.append(index)

#format for experiment input
df = pd.DataFrame({'id':id, 'munsell':sorted_munsell, 'rgb':sorted_rgb})
print(df)

#---------------------------------------------------------------------------------
# take every 8th value and append it to transpose color grid
ordered_munsell = []
ordered_rgb = []
R8 = np.array([0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80])

for val in range(8):
    color8 = R8 + val
    for i in range(len(sorted_munsell)):
        if i in color8:
            ordered_munsell.append(sorted_munsell[i])
            ordered_rgb.append(sorted_rgb[i])

#---------------------------------------------------------------------------------
# make dataframe with all these columns
df = pd.DataFrame({'Munsell':ordered_munsell, 'RGB':ordered_rgb})

id = []
for index, row in df.iterrows():
    id.append(index)

#format for experiment input
df = pd.DataFrame({'id':id, 'munsell':ordered_munsell, 'rgb':ordered_rgb})
print(df)

# save df as csv
df.to_csv('gibson-et-al-RGB-conversions-munsell-sorted-V1.csv', index=False)

# save df as csv
df.to_json('munsell-gibson-V1-sorting.json', orient='records')







#---------------------------------------------------------------------------------
# NOT USED
#---------------------------------------------------------------------------------
# R10 = np.array([0, 20, 40, 60, 80])
# R5 = np.array([10, 30, 50, 70])
# # SORTING VERSION 2: GROUP COLOR TOGETHER BY WHERE IT IS ON HUE BAND
# # (I.E. ALL 10R's THEN ALL 5R's, ALL 10YR's THEN ALL 5YR's)
# sorted_munsell = []
# sorted_rgb = []
# for val in range(10):
#     color10 = R10 + val
#     color5 = R5 + val
#     for i in range(len(munsell)):
#         if i in color10:
#             sorted_munsell.append(munsell[i])
#             sorted_rgb.append(rgb[i])
#     for i in range(len(munsell)):
#         if i in color5:
#             sorted_munsell.append(munsell[i])
#             sorted_rgb.append(rgb[i])
#
#
# #---------------------------------------------------------------------------------
# # make dataframe with all these columns
# df2 = pd.DataFrame({'Munsell':sorted_munsell, 'RGB':sorted_rgb})
#
# id = []
# for index, row in df2.iterrows():
#     id.append(index)
#
# #format for experiment input
# df2 = pd.DataFrame({'id':id, 'munsell':sorted_munsell, 'rgb':sorted_rgb})
# # print(df2)
#
# # # save df as csv
# # df2.to_csv('gibson-et-al-RGB-conversions-munsell-sorted-V2.csv', index=False)
#
# # # save df as csv
# # df2.to_json('munsell-gibson-V2-sorting.json', orient='records')









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

# #---------------------------------------------------------------------------------
# # make dataframe with all these columns
# df = pd.DataFrame({'Munsell':sorted_munsell, 'RGB':sorted_rgb})

# formatted_rgb = []
# for index, row in df.iterrows():
#     formatted_rgb.append("(" + str(int(row['RGB'][0]*255)) + ", " + str(int(row['RGB'][1]*255)) + ", " + str(int(row['RGB'][2]*255)) + ")")

# id = []
# for index, row in df.iterrows():
#     id.append(index)

# #format for experiment input
# df = pd.DataFrame({'id':id, 'munsell':sorted_munsell, 'rgb':formatted_rgb})

#---------------------------------------------------------------------------------
# save df as csv
#df.to_csv('gibson-et-al-RGB-conversions-sorted.csv', index=False)

# # save df as csv
# df.to_json('munsell-gibson.json', orient='records')
