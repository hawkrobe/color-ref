import csv
import numpy as np
import colormath
import pandas as pd
import seaborn as sns
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor

#---------------------------------------------------------------------------------
# INITIALIZE DATA

# LOAD COLOR PICKER DATA FOR BLOCK 2 (EXPECTATION RESPONSES)
df = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
# select columns for word, button response, and condition (which block)
cols = ["word", "aID", "response_r", "response_g", "response_b", "condition"]
df = df[cols]

# select trials by block
df_block1 = df[df['condition'] == 'block1_target_trial']
df_block2 = df[df['condition'] == 'block2_target_trial']

# LOAD ORDERED LIST OF WORDS BY ENTROPY for BLOCK 2 RESPONSES
df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-block2.csv')
words = df_entropy['word'].to_list()

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS
#---------------------------------------------------------------------------------

def selectRGBPoints(df, word):
    # select responses for this word
    points = df[df['word'] == word]
    # sort by participant ID to get all values in the same order
    points = points.sort_values(by=['aID'])
    # return points['aID'].to_list()
    return points['response_r'].to_list(), points['response_g'].to_list(), points['response_b'].to_list()

# convert RGB points to LAB
def RGBtoLAB(r, g, b):
    lab_points = np.empty([len(r),3])
    for i in range(len(r)):
        # convert to [0,1] scaled rgb values
        c = (float(r[i])/255, float(g[i])/255, float(b[i])/255)
        # create RGB object
        rgb = sRGBColor(c[0], c[1], c[2])
        # convert
        lab = convert_color(rgb, LabColor)
        # get RGB values from object
        lab = lab.get_value_tuple()
        # store in array
        lab_points[i, 0] = lab[0]
        lab_points[i, 1] = lab[1]
        lab_points[i, 2] = lab[2]

    return lab_points

def getDistance(points1, points2):
    diff_squared = (points1-points2)**2
    return np.sqrt(np.sum(diff_squared, 1))

def binarize(a):
    # if this element is 0, block1 and block2 responses for this participant
    # matched
    if a == 0:
        return 1
    # if this element anything else, block1 and block2 responses for this
    # participant did NOT match
    else:
        return 0

#---------------------------------------------------------------------------------
# compute distances between each participant's block1-block2 response for each word
# output should be a distance

df_output = pd.DataFrame()

for index, word in enumerate(words):
    # get rgb responses for each block
    r1, g1, b1 = selectRGBPoints(df_block1, word)
    r2, g2, b2 = selectRGBPoints(df_block2, word)

    lab1 = RGBtoLAB(r1, g1, b1)
    lab2 = RGBtoLAB(r2, g2, b2)

    # get distances between block1 and block2 responses for each participant
    dists = getDistance(lab1, lab2).tolist()

    # binarize distances for logistic regression
    vfunc = np.vectorize(binarize)
    isMatch = vfunc(dists)

    dfWords = [word] * len(dists)
    to_append = pd.DataFrame({'word':dfWords, 'distances':dists, 'isMatch':isMatch}, columns=['word', 'distances', 'isMatch'])

    df_output = df_output.append(to_append, ignore_index=True)

df_output.to_csv("./intra-participant/block1-block2-dists.csv", index=False)

print(words[:10] + words[-10:])
