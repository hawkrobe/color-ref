import csv
import numpy as np
import colormath
import pandas as pd
import seaborn as sns
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
from colormath.color_diff import delta_e_cie2000

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

# get rgb points in order of participant id; output = lists
def selectRGBPoints(df, word):
    # select responses for this word
    points = df[df['word'] == word]
    # sort by participant ID to get all values in the same order
    points = points.sort_values(by=['aID'])
    # return points['aID'].to_list()
    return points['aID'].to_list(), points['response_r'].to_list(), points['response_g'].to_list(), points['response_b'].to_list()

# convert RGB points to LAB; output = numpy
def RGBtoLAB(r, g, b):
    lab = np.empty([len(r),], dtype=object)
    for i in range(len(r)):
        # convert to [0,1] scaled rgb values
        c = (float(r[i])/255, float(g[i])/255, float(b[i])/255)
        # create RGB object
        rgb = sRGBColor(c[0], c[1], c[2])
        # convert
        lab[i] = convert_color(rgb, LabColor)

    return lab

# use Delta E (most complex + accurate color algorithm)
# https://python-colormath.readthedocs.io/en/latest/delta_e.html
# http://zschuessler.github.io/DeltaE/learn/
def getDeltaE(lab1, lab2):
    return delta_e_cie2000(lab1, lab2, Kl=1, Kc=1, Kh=1)


#---------------------------------------------------------------------------------
# compute deltaE between each participant's block1-block2 response for each word
# output should be a distance

df_output = pd.DataFrame()
ids = np.arange(0, 100, 1)

for index, word in enumerate(words):
    # get rgb responses for each block
    aID1, r1, g1, b1 = selectRGBPoints(df_block1, word)
    aID2, r2, g2, b2 = selectRGBPoints(df_block2, word)

    lab1 = RGBtoLAB(r1, g1, b1)
    lab2 = RGBtoLAB(r2, g2, b2)

    # vectorize Delta E function
    vectorizedDeltaE = np.vectorize(getDeltaE)

    # calculate Delta E between lab1 and lab2 numpy arrays using vectorized deltaE function
    deltaE = vectorizedDeltaE(lab1, lab2)
    dfWords = [word] * len(deltaE)

    to_append = pd.DataFrame({'word':dfWords, 'aID': aID1, 'deltaE':deltaE}, columns=['word', 'aID', 'deltaE'])

    df_output = df_output.append(to_append, ignore_index=True)

print(df_output)
df_output.to_csv("./intra-participant/block1-block2-deltaE.csv", index=False)
