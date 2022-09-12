import csv
import numpy as np
import colormath
import pandas as pd
import json
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib
import colorsys
import seaborn as sns
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor

#===============================================================================
# FIGURE 1: color response visualization
#===============================================================================

# LOAD ALL COLOR PICKER DATA
df = pd.read_csv(r'../data/norming/color.csv')
# select columns for word and RGB color response
cols = ["word", "button_pressed", "response_munsell", "response_r", "response_g", "response_b", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block1_target_trial']
block = "both"

# LOAD ORDERED LIST OF WORDS BY ENTROPY
df_entropy = pd.read_csv('./experiment1/analysis1/sorted-entropy-both.csv')
words = df_entropy['word'].to_list()

#-------------------------------------------------------------------------------
# HELPER FUNCTIONS

# function to select all button responses that belong to a particular target words
def selectResponses(df, word):
    points = df[df['word'] == word]
    return points['button_pressed'].to_list()

# Step sorting function as defined by:
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

def plotSwatches(words, condition):
    width= 15
    height= 7
    numChoices = 88
    rgbVals = []
    munsellVals = []

    fig, ax = plt.subplots(len(words), 1, figsize=(width,height), frameon=False)

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
        rgb.sort(key=lambda(r,g,b): stepSort(r,g,b,8))

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
                ax[index].add_patch(patches.Rectangle(pos, w, h, color=rgb[c], linewidth=0))
                # increment to next color in rgb array
                c += 1

            # start next block at previous x + width of rectangle this rectangle
            x += w

            ax[index].get_xaxis().set_ticks([])
            ax[index].get_yaxis().set_ticks([])
            ax[index].set_ylabel(word, fontsize='medium', rotation='horizontal', ha='right')

    plt.savefig('./experiment1/figures/stepSort-allResponses-%s.pdf' % condition,bbox_inches='tight',dpi=300)
    plt.show()

#-------------------------------------------------------------------------------
# CALL WITH BOTH WORD SETS

plotSwatches(words[:10], 'concrete') # first 10 (least entropy) words
plotSwatches(words[-10:], 'abstract') # last 10 (highest entropy) words
