import csv
import numpy as np
import colormath
import pandas as pd
import json
import random
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
#---------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib
import colorsys

#---------------------------------------------------------------------------------
# INITIALIZE DATA
#---------------------------------------------------------------------------------

# LOAD ALL COLOR PICKER DATA
df = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
# select columns for word and RGB color response
cols = ["word", "button_pressed", "response_munsell", "response_r", "response_g", "response_b", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block1_target_trial']
block = "both"

# LOAD ORDERED LIST OF WORDS BY ENTROPY
df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-%s.csv' % block)
df_entropy = df_entropy.rename(columns={block: "entropy"})
words = df_entropy['word'].to_list()

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS
#---------------------------------------------------------------------------------

# function to select all button responses that belong to a particular target words
def selectResponses(df, word):
    points = df[df['word'] == word]
    return points['button_pressed'].to_list()

# # convert RGB points to HSV
# def RGBtoHSV(r, g, b):
#     hsv_points = np.empty([len(r),3])
#     for i in range(len(r)):
#         # convert to [0,1] scaled rgb values
#         c = (float(r[i])/255, float(g[i])/255, float(b[i])/255)
#         # create RGB object
#         rgb = sRGBColor(c[0], c[1], c[2])
#         # convert
#         hsv = convert_color(rgb, HSVColor)
#         # get RGB values from object
#         hsv = hsv.get_value_tuple()
#         # store in array
#         hsv_points[i, 0] = hsv[0]
#         hsv_points[i, 1] = hsv[1]
#         hsv_points[i, 2] = hsv[2]
#
#     return hsv_points
#
# # convert HSV to RGB
# def HSVtoRGB(hsv_points):
#     sorted_rgb = np.empty([len(hsv_points),], dtype=object)
#     for i in range(len(hsv_points)):
#         # create HSV object
#         hsv = HSVColor(hsv_points[i,0], hsv_points[i,1], hsv_points[i,2])
#         # convert HSV to RGB object
#         rgb = convert_color(hsv, sRGBColor)
#         # get RGB values from object
#         rgb = rgb.get_value_tuple()
#         # store in array
#         sorted_rgb[i] = rgb
#
#     return sorted_rgb

# https://www.alanzucconi.com/2015/09/30/colour-sorting/
def stepSort(r,g,b, repetitions=1):
    lum = math.sqrt( .241 * r + .691 * g + .068 * b )

    h, s, v = colorsys.rgb_to_hsv(r,g,b)

    h2 = int(h * repetitions)
    lum2 = int(lum * repetitions)
    v2 = int(v * repetitions)

    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum

    return (h2, lum, v2)


#---------------------------------------------------------------------------------
# STEP 1: RGB --> HSV, sort by hue, sorted-HSV --> RGB
#---------------------------------------------------------------------------------
width= 15
height= 10
numChoices = 88
rgbVals = []
munsellVals = []
condition = 'concrete'

# first 10 (least entropy) words
# last 10 (highest entropy) words
words = words[-10:] if condition == 'abstract' else words[:10] 
fig, ax = plt.subplots(len(words), 1, figsize=(width,height))

#--------------------------------------------
# read json file with all munsell/rgb values for each button response
with open('../experiments/normingTask/json-data-files/munsell-gibson-V1-sorting.json') as f:
  data = json.load(f)

  for j in range(len(data)):
      rgbVals.append(eval(data[j].items()[0][1]))
      munsellVals.append(data[j].items()[1][1])

# print(rgbVals)

#--------------------------------------------
for index, word in enumerate(words):
    print(word)
    rgb = []
    greys = []
    percentage = []
    rgbDict = {} # keep track of index of response of a particular color

    responses = selectResponses(df, word)

    # for each button response, count number of responses for that particular button color
    # divide it by total number of responses to get percentage of bar
    for i in range(numChoices):
        numResponses = responses.count(i)

        p = float(numResponses)/float(len(responses))
        percentage.append(p)


        # if there's a response for this button response #
        if numResponses != 0:
            colorList = [float(rgbVals[i][0])/255, float(rgbVals[i][1])/255, float(rgbVals[i][2])/255] # 0-255 scale
            colorTuple = (float(rgbVals[i][0])/255, float(rgbVals[i][1])/255, float(rgbVals[i][2])/255)

            # store TUPLE version of color in rgb dict
            # key = to the rgb value, value = index in possible choices
            rgbDict[colorTuple] = i

            # if this color is not greyscale, add LIST version to rgb values to step sort
            if munsellVals[i][0] != 'N':
                rgb.append(colorList)

            # if a shade of grey, add LIST version to separate array to be concatenated at end
            else:
                greys.append(colorList)


    # step sort the non-greyscale colors
    rgb.sort(key=lambda r,g,b: stepSort(r,g,b,8))

    # concatenate reversed greyscale values to the sorted colors array
    rgb = rgb + greys[::-1]


    # since we can't sort the percentage list using the stepSort function (different input types)
    # iterate over rgbDict -> key = color, value = index of desired element of
    # the percentage list -> append this value to a new list (widths)
    widths = []
    for color in rgb:
        # convert color to tuple
        t = (color[0], color[1], color[2])

        widths.append(percentage[rgbDict[t]])

    #--------------------------------------------
    # make plots
    #--------------------------------------------
    x = 0
    y = 0
    w = 0.005
    h = 1
    c = 0

    # iterate over percentage values for this word
    # X percent of the bar should be of color associated with that button response
    for w in widths:

        pos = (x, y)
        # if this index in possible choices has a percentage value associated with it
        # add a patch for this color proportional to it's percentage response
        if width != 0:
            ax[index].add_patch(patches.Rectangle(pos, w, h, color=rgb[c]))
            # increment to next color in rgb array
            c += 1

        # start next block at previous x + width of rectangle this rectangle
        x += w

        ax[index].get_xaxis().set_ticks([])
        ax[index].get_yaxis().set_ticks([])
        ax[index].set_ylabel(word, fontsize='x-small', rotation='horizontal', ha='right')


plt.savefig('./plots/stepSort-allResponses-{}.pdf'.format(condition),
            bbox_inches='tight',dpi=300)
