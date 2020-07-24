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
import gensim
import random
import math
import scipy
import gensim.downloader as api
from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import get_tmpfile
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

#---------------------------------------------------------------------------------
# STEP 1: Estimate a Gaussian for each word from the points for that word
# https://cmsc426.github.io/colorseg/ 

# missing "bird"
words = ['dog', 'mortal', 'big', 'adjective', 'religion', 'rain', 'lime', 'noun', 'angry', 'cloud', 'door', 'justice', 'berry', 'sad', 'tree', 'verb', 'existence', 'running', 'sky', 'fun', 'soaring', 'pain', 'equality', 'universe']

#store means
all_means = np.empty([len(words), 3])
#store covariance matrices
all_covariance = np.empty([len(words), 3, 3])
# store variances
all_variances = np.empty([len(words),])

# iterate over all words
unsorted_variances = open("unsorted-variances.txt", "w+")
for index, word in enumerate(words):
    with open('%s.txt' % (word)) as fp: 
        # get points associated with word
        points = fp.readlines()
        fp.close()

    # store each point in a numpy array of dimensions num_points x LAB
    point_matrix = np.empty([len(points),3])
    for line_num, point in enumerate(points):
        point = point.split(" ")
        point_matrix[line_num, 0] = float(point[0])
        point_matrix[line_num, 1] = float(point[1])
        point_matrix[line_num, 2] = float(point[2][:-1])

    # estimate parameters (mean and covariance) of the likelihood gaussian distribution
    mean = np.mean(point_matrix, axis=0)
    # store mean
    all_means[index,:] = mean

    product = np.matmul(np.transpose(point_matrix - mean), point_matrix - mean)
    covariance = product/len(points)
    # store covariance matrix
    all_covariance[index, :, :] = covariance

    # STEP 2: Calculate variance of each word's Gaussian from its covariance matrix
    variance = covariance.trace()
    all_variances[index] = variance
    unsorted_variances.write('%s: %d\n' % (word, variance))

unsorted_variances.close()

# STEP 3: sort words in order of ascending variance
argsorted = np.argsort(all_variances)
print(argsorted)
sorted = np.sort(all_variances)
print(sorted)

sorted_variances = open("sorted-variances.txt", "w+")
# ordered_words = np.empty([len(words),], dtype=object)
for i, index in enumerate(argsorted):
    # ordered_words[i] = words[index]
    sorted_variances.write('%s: %d\n' % (words[index], sorted[i]))

# print(ordered_words)
sorted_variances.close()

#---------------------------------------------------------------------------------

