import random
import numpy as np
import colormath
import matplotlib.pyplot as plt
import statistics
import math
import scipy
import pandas as pd
from collections import defaultdict
from mpl_toolkits.mplot3d import axes3d, Axes3D
from statistics import mean
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import entropy

# #---------------------------------------------------------------------------------
# STEP 0: make points x LAB array of dummy points

df = pd.read_csv(r'../data/norming/colorPickerData-0.csv')
# select columns for word and RGB color response
cols = ["word", "button_pressed", "response_munsell", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block2_target_trial']
block = "both"
wordSet = "set0"

# identify target words
uniqueWords = set(df['word'].to_list())
colorWords = set(['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink'])
targetWords = list(uniqueWords-colorWords)

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS

# function to select all responses that belong to a particular target word
def selectWordResponses(df, word):
    points = df[df['word'] == word]
    return points['button_pressed'].to_list()


#---------------------------------------------------------------------------------
numChoices = 88
# initialize numWords (20) x numColors (88) array
countMatrix = np.empty([len(targetWords), numChoices], dtype=float)
entropies = np.empty([len(targetWords),])

for index, word in enumerate(targetWords):
    responses = np.array(selectWordResponses(df, word))

    pseudoCount = 1.0/len(responses)

    # count number of responses for each color for this word
    # remove 0's by adding psuedo counts of 1/numObservations
    # divide by number of choices to get probability
    countMatrix[index,:] = [(np.count_nonzero(responses == i) + pseudoCount)/numChoices for i in range(88)]
    # calculate entropy
    entropies[index] = scipy.stats.entropy(countMatrix[index,:], base=2)

#---------------------------------------------------------------------------------
# sort words in order of ascending entropy
argsorted = np.argsort(entropies)
sortedWords = np.array(targetWords)[argsorted]
sortedEntropies = np.sort(entropies)

df2 = pd.DataFrame({'word':sortedWords, block:sortedEntropies})
cols = ['word', block]
df2 = df2[cols]
print(df2)
# save df as csv
df2.to_csv("./entropy/sorted-entropies-%s-%s.csv" % (wordSet, block), index=False)
