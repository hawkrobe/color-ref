#---------------------------------------------------------------------------------
# Modify the Bayesian representativeness model code to estimate a Gaussian from
# the human annotation data points instead of the image data points
#---------------------------------------------------------------------------------

import random
import csv
import numpy as np
import colormath
import matplotlib.pyplot as plt
import statistics
import math
import scipy
from collections import defaultdict
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
from mpl_toolkits.mplot3d import axes3d, Axes3D
from statistics import mean
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import multivariate_normal
from scipy.special import logsumexp
from scipy.stats import rankdata
import pandas as pd

#---------------------------------------------------------------------------------
# STEP 0: Process data

# process data csv into pandas dataframe
df = pd.read_csv(r'../data/norming/colorPickerData-0.csv')
# select columns for word and RGB color response
cols = ["word", "response_r", "response_g", "response_b", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
df = df[df['condition'] == 'block1_target_trial']
block = "block1"
wordSet = "wordSet0"


# identify target words
uniqueWords = set(df['word'].to_list())
colorWords = set(['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink'])
targetWords = list(uniqueWords-colorWords)
print(targetWords)

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS

# function to select all RGB points that belong to a particular target words
def selectRGBPoints(df, word):
    points = df[df['word'] == word]
    return points['response_r'].to_list(), points['response_g'].to_list(), points['response_b'].to_list()


# convert RGB points to LAB
def convertToLAB(r, g, b):
    labTuples = np.empty([len(r),], dtype=object)
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
        labTuples[i] = lab

    return labTuples

#---------------------------------------------------------------------------------
# STEP 1: Estimate a Gaussian for each word from the points for that word
# https://cmsc426.github.io/colorseg/

unsorted_variances = open("unsorted-variances-%s-%s.txt" % (wordSet, block), "w+")
all_means = np.empty([len(targetWords), 3]) #store means
all_covariance = np.empty([len(targetWords), 3, 3]) #store covariance matrices
all_variances = np.empty([len(targetWords),]) # store variances

for index, word in enumerate(targetWords):
    r, g, b = selectRGBPoints(df, word)
    labTuples = convertToLAB(r, g, b)

    # store each point in a numpy array of dimensions num_points x LAB
    point_matrix = np.empty([len(labTuples),3])
    for line_num, point in enumerate(labTuples):
        point_matrix[line_num, 0] = labTuples[line_num][0]
        point_matrix[line_num, 1] = labTuples[line_num][1]
        point_matrix[line_num, 2] = labTuples[line_num][2]

    # estimate parameters (mean and covariance) of the likelihood gaussian distribution
    mean = np.mean(point_matrix, axis=0)
    # store mean
    all_means[index,:] = mean

    product = np.matmul(np.transpose(point_matrix - mean), point_matrix - mean)
    covariance = product/len(labTuples)
    # store covariance matrix
    all_covariance[index, :, :] = covariance

    # STEP 2: Calculate variance of each word's Gaussian from its covariance matrix
    variance = covariance.trace()
    all_variances[index] = variance
    unsorted_variances.write('%s: %d\n' % (word, variance))

unsorted_variances.close()

# # STEP 3: sort words in order of ascending variance
# argsorted = np.argsort(all_variances)
# print(argsorted)
# sorted = np.sort(all_variances)
# print(sorted)
#
# sorted_variances = open("sorted-variances.txt", "w+")
# # ordered_words = np.empty([len(words),], dtype=object)
# for i, index in enumerate(argsorted):
#     # ordered_words[i] = words[index]
#     sorted_variances.write('%s: %d\n' % (words[index], sorted[i]))
#
# # print(ordered_words)
# sorted_variances.close()

#---------------------------------------------------------------------------------
