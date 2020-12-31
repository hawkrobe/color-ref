#---------------------------------------------------------------------------------
# Get pairwise delta E values (using CIE2000 metric) for each word's block1
# and block2 responses
#---------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------
# identify target words (no particular order)
uniqueWords = set(df['word'].to_list())
colorWords = set(['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink'])
words = list(uniqueWords-colorWords)

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
    return points['response_r'].to_list(), points['response_g'].to_list(), points['response_b'].to_list()

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
def getDeltaE(allLabs, thisLab):
    return delta_e_cie2000(thisLab, allLabs, Kl=1, Kc=1, Kh=1)

#---------------------------------------------------------------------------------
# compute distances between each participant's block2 response for each word
# output should be a distance

#--------------------------------
# change block + select corresponding data frame
block = "block2"
df = df_block2
#--------------------------------
avgDeltaE = np.empty([len(words),])

for index, word in enumerate(words):
    print(word)
    # get rgb responses for all participants' block 2 responses for this word
    r, g, b = selectRGBPoints(df, word)
    # get lab objects for these rgb values
    lab = RGBtoLAB(r, g, b)

    # vectorize Delta E function
    vectorizedDeltaE = np.vectorize(getDeltaE)

    n = lab.shape[0]
    deltaE = np.empty([n, n])
    # loop over every lab object for this word, and calculate Delta E with
    # every other lab object
    for i in range(n):
        deltaE[i,:] = vectorizedDeltaE(lab, lab[i])

    # # check if matrix is symmetric: yes
    # print(np.allclose(deltaE, deltaE.T, rtol=1e-05, atol=1e-08))
    # print(np.count_nonzero(deltaE))

    # extract only the upper triangular elements
    upperTriangleElements = deltaE[np.triu_indices(n)]

    # print(deltaE.shape)
    # print(len(upperTriangleElements))

    # get average deltaE for the responses for this word
    avgDeltaE[index] = np.mean(upperTriangleElements)

#---------------------------------------------------------------------------------
# sort words in order of ascending average DeltaE
argsorted = np.argsort(avgDeltaE)
sortedWords = np.array(words)[argsorted]
sortedDeltaE = np.sort(avgDeltaE)
print(sortedWords)

df_output = pd.DataFrame({'word':sortedWords, 'Delta-E-CIE-2000':sortedDeltaE}, columns=['word', 'Delta-E-CIE-2000'])
print(df_output)
# save df as csv
df_output.to_csv("./deltaE/sorted-deltaE-CIE2000-%s.csv" % block, index=False)
