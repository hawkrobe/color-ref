#===============================================================================
# ANALYSIS 1: variability measures vs. word ratings

# INPUT: colorPickerData-all.csv, GlasgowNorms.xlsx

# OUTPUTS:
# entropy (both blocks): sorted-variance-both.csv
# variance (both blocks): sorted-entropy-both.csv
# deltaE (block1): sorted-deltaE-block1.csv
# compiled variability measures + word ratings: compiled-variabilityMeasures-glasgowRatings.csv
#-------------------------------------------------------------------------------
# ANALYSIS 2: intra-participant

# INPUT: colorPickerData-all.csv

# OUTPUT:
# deltaE (between both blocks): block1-block2-deltaE.csv
#-------------------------------------------------------------------------------
# ANALYSIS 3: expectation

# INPUT: colorPickerData-all.csv, expectationData-all.csv

# OUTPUTS:
# slider ratings by condition: expectation-by-condition.csv
# ground truth by condition: ground-truth-by-condition.csv
# logistic regression on participant match (block2): logistic-regression.csv
# deltaE: sorted-deltaE-block2.csv
#===============================================================================

import csv
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib
import scipy
import colormath
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
from colormath.color_diff import delta_e_cie2000
from statistics import mean
from scipy.stats import entropy
#-------------------------------------------------------------------------------
# LOAD DATA

dfColor = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
cols = ["word", "aID", "button_pressed", "response_munsell", "response_r", "response_g", "response_b", "condition"]
dfColor = dfColor[cols]

# Change condition to select different blocks
dfColor_block1 = dfColor[dfColor['condition'] == 'block1_target_trial']
dfColor_block2 = dfColor[dfColor['condition'] == 'block2_target_trial']
dfColor_both = dfColor

# identify target words
uniqueWords = set(dfColor['word'].to_list())
colorWords = set(['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink'])
targetWords = list(uniqueWords-colorWords)

#===============================================================================
# ANALYSIS 1: measures of variability + word ratings
#===============================================================================

# HELPER FUNCTIONS

# function to select all data of type in df for word
def selectData(df, word, type):
    points = df[df['word'] == word]
    # sort by participant ID to get all values in the same order
    points = points.sort_values(by=['aID'])
    return points[type].to_list()

# convert RGB points to LAB, output = numpy array of LAB tuples
def RGBtoLABTuples(r, g, b):
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

# convert RGB points to LAB, output = numpy array of LAB objects
def RGBtoLABObject(r, g, b):
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
def computeDeltaE(allLabs, thisLab):
    return delta_e_cie2000(thisLab, allLabs, Kl=1, Kc=1, Kh=1)

# get delta E for df of a particular block's response
def getDeltaE(df):
    avgDeltaE = np.empty([len(targetWords),])

    for index, word in enumerate(targetWords):
        # get rgb responses for all participants' block 2 responses for this word
        r, g, b = selectData(df, word, 'response_r'), selectData(df, word, 'response_g'), selectData(df, word, 'response_b')
        # get lab objects for these rgb values
        lab = RGBtoLABObject(r, g, b)

        # vectorize Delta E function
        vectorizedDeltaE = np.vectorize(computeDeltaE)

        n = lab.shape[0]
        deltaE = np.empty([n, n])
        # loop over every lab object for this word, and calculate Delta E with
        # every other lab object
        for i in range(n):
            deltaE[i,:] = vectorizedDeltaE(lab, lab[i])

        # extract only the upper triangular elements
        upperTriangleElements = deltaE[np.triu_indices(n)]

        # get average deltaE for the responses for this word
        avgDeltaE[index] = np.mean(upperTriangleElements)

    return avgDeltaE

#-------------------------------------------------------------------------------
# VARIANCE ESTIMATES: calculated off responses from both blocks

# STEP 1: Estimate a Gaussian for each word from the points for that word
# https://cmsc426.github.io/colorseg/

all_means = np.empty([len(targetWords), 3]) #store means
all_covariance = np.empty([len(targetWords), 3, 3]) #store covariance matrices
all_variances = np.empty([len(targetWords),]) # store variances

for index, word in enumerate(targetWords):
    r, g, b = selectData(dfColor_both, word, 'response_r'), selectData(dfColor_both, word, 'response_g'), selectData(dfColor_both, word, 'response_b')
    labTuples = RGBtoLABTuples(r, g, b)

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

# STEP 3: sort words in order of ascending variance
argsortedVariances = np.argsort(all_variances)
sortedWords_variance = np.array(targetWords)[argsortedVariances]
sortedVariances = np.sort(all_variances)

dfVariance = pd.DataFrame({'word':sortedWords_variance, 'variance':sortedVariances}, columns=['word', 'variance'])
print(dfVariance)
# save df as csv
dfVariance.to_csv("./experiment1/analysis1/sorted-variance-both.csv", index=False)

#-------------------------------------------------------------------------------
# ENTROPY: calculated off responses from both blocks

numChoices = 88
# initialize numWords x numColors (88) array
counts = np.empty([len(targetWords), numChoices], dtype=float)
probabilities = np.empty([len(targetWords), numChoices], dtype=float)
entropies = np.empty([len(targetWords),])

for index, word in enumerate(targetWords):
    responses = np.array(selectData(dfColor_both, word, 'button_pressed'))

    pseudoCount = 1/numChoices # Schurmann-Grassberger estimator

    # count number of responses for each color for this word by adding
    # psuedo counts of 1/numChoices to every cell
    counts[index,:] = [(np.count_nonzero(responses == i) + pseudoCount) for i in range(numChoices)]

# normalize by dividing by total updated counts for that word
for index, word in enumerate(targetWords):
    probabilities[index,:] = counts[index,:]/np.sum(counts[index,:])

    # calculate entropy
    entropies[index] = scipy.stats.entropy(probabilities[index,:], base=2)

# sort words in order of ascending entropy
argsortedEntropies = np.argsort(entropies)
sortedWords_entropy = np.array(targetWords)[argsortedEntropies]
sortedEntropies = np.sort(entropies)

dfEntropy = pd.DataFrame({'word':sortedWords_entropy, 'entropy':sortedEntropies}, columns=['word', 'entropy'])
print(dfEntropy)
# save df as csv
dfEntropy.to_csv("./experiment1/analysis1/sorted-entropy-both.csv", index=False)

#-------------------------------------------------------------------------------
# DELTA E (CIE2000): calculated off responses from block 1
# caution! takes a while to run

# avgDeltaE_block1 = getDeltaE(dfColor_block1)
# # sort words in order of ascending average DeltaE
# argsorted = np.argsort(avgDeltaE_block1)
# sortedWords = np.array(targetWords)[argsorted]
# sortedDeltaE_block1 = np.sort(avgDeltaE_block1)
#
# dfDeltaE = pd.DataFrame({'word':sortedWords, 'deltaE':sortedDeltaE_block1}, columns=['word', 'deltaE'])
# print(dfDeltaE)
# # save df as csv
# dfDeltaE.to_csv("./experiment1/analysis1/sorted-deltaE-block1.csv", index=False)

#-------------------------------------------------------------------------------
# COMPILE ALL METRICS

dfGlasgow = pd.read_excel(r'./experiment1/GlasgowNorms.xlsx')
dfGlasgow = dfGlasgow.rename(columns={'Unnamed: 0': 'word'})
cols = ['word', 'IMAG', 'CNC', 'FAM']
dfGlasgow = dfGlasgow[cols]

imag = []
cnc = []
count = 0
original = []
for w in targetWords:
    # handle known anomalies
    if w == 'bunkbed':
        i = dfGlasgow['IMAG'][dfGlasgow['word'] == 'bunk (bed)']
        imag.append(i.tolist()[0])
        c = dfGlasgow['CNC'][dfGlasgow['word'] == 'bunk (bed)']
        cnc.append(c.tolist()[0])
        original.append('Y')
    elif w == 'flag':
        # print('%s not found' % w)
        imag.append("N/A")
        cnc.append("N/A")
        original.append('N/A')

    # base case: word exists in Glasgow set in its original form
    elif dfGlasgow['word'].str.contains(w).any():
        i = dfGlasgow['IMAG'][dfGlasgow['word'] == w]
        imag.append(i.tolist()[0])
        c = dfGlasgow['CNC'][dfGlasgow['word'] == w]
        cnc.append(c.tolist()[0])
        original.append('Y')

    # else, not found at all
    else:
        count +=1
        imag.append("N/A")
        cnc.append("N/A")
        original.append('N/A')

print("ratings do not exist for %d out of %d words" % (count, len(targetWords)))

# caution! requires avgDeltaE which takes a while to run
# dfCompiled = pd.DataFrame({'word':targetWords, 'entropy':entropies, 'variance':all_variances, 'deltaE':avgDeltaE_block1, 'imageability':imag, 'concreteness':cnc},
# columns=['word', 'entropy', 'variance', 'deltaE', 'imageability', 'concreteness'])
# print(dfCompiled)
# dfCompiled.to_csv("./experiment1/analysis1/compiled-variabilityMeasures-glasgowRatings.csv", index=False)

#-------------------------------------------------------------------------------
# ANALYZE ORDERING BY EACH METRIC
# check if the top 99 words (least entropy and least variance) in the sorted variances and sorted entropies are the same
concrete_entp = set(sortedWords_entropy[0:99])
concrete_var = set(sortedWords_variance[0:99])
print("words in bottom 50% ENTP (least entropy) but not in bottom 50% VAR (highest variance)")
print(concrete_entp - concrete_var)
print("%d of %d words are different" % (len(concrete_entp - concrete_var), len(concrete_entp)))
print("")
print("words in bottom 50% VAR (least variance) but not in bottom 50% ENTP (highest entropy)")
print(concrete_var - concrete_entp)
print("%d of %d words are different" % (len(concrete_var - concrete_entp), len(concrete_entp)))

#===============================================================================
# ANALYSIS 2: intra-participant analysis
#===============================================================================

# compute deltaE between each participant's block1-block2 response for each word
dfIntraparticipant = pd.DataFrame()

# iterate over words sorted by entropy
for index, word in enumerate(sortedWords_entropy):
    # get rgb responses for each block
    aID1, r1, g1, b1 = selectData(dfColor_block1, word, 'aID'), selectData(dfColor_block1, word, 'response_r'), selectData(dfColor_block1, word, 'response_g'), selectData(dfColor_block1, word, 'response_b')
    aID2, r2, g2, b2 = selectData(dfColor_block2, word, 'aID'), selectData(dfColor_block2, word, 'response_r'), selectData(dfColor_block2, word, 'response_g'), selectData(dfColor_block2, word, 'response_b')

    lab1 = RGBtoLABObject(r1, g1, b1)
    lab2 = RGBtoLABObject(r2, g2, b2)

    # vectorize Delta E function
    vectorizedDeltaE = np.vectorize(computeDeltaE)

    # calculate Delta E between lab1 and lab2 numpy arrays using vectorized deltaE function
    deltaE = vectorizedDeltaE(lab1, lab2)
    dfWords = [word] * len(deltaE)

    to_append = pd.DataFrame({'word':dfWords, 'aID': aID1, 'deltaE':deltaE}, columns=['word', 'aID', 'deltaE'])
    dfIntraparticipant = dfIntraparticipant.append(to_append, ignore_index=True)

print(dfIntraparticipant)
dfIntraparticipant.to_csv("./experiment1/analysis2/block1-block2-deltaE.csv", index=False)

#===============================================================================
# ANALYSIS 3: expectation analysis
#===============================================================================

# LOAD ALL EXPECTATION RATING DATA
dfExpectation = pd.read_csv(r'../data/norming/expectationData-all.csv')
cols = ["word", "aID", "sliderResponse"]
dfExpectation = dfExpectation[cols]

#-------------------------------------------------------------------------------
# ADD COLUMN FOR CONDITION

expectationCondition = []
concrete = sortedWords_entropy[:100]
abstract = sortedWords_entropy[-100:]

for index, row in dfExpectation.iterrows():
    if row['word'] in concrete:
        expectationCondition.append('concrete')
    else:
        expectationCondition.append('abstract')

# add condition column to df
dfExpectation['condition'] = expectationCondition
dfExpectation.to_csv("./experiment1/analysis3/expectation-by-condition.csv", index=False)

#-------------------------------------------------------------------------------
# COMPUTE GROUND TRUTH

dfWords = []
groundTruth = []
groundTruthCondition = []
# get percentages of response for each possible choice
for word_index, word in enumerate(sortedWords_entropy):
    numChoices = 88
    responses = selectData(dfColor_block2, word, 'button_pressed')

    # for each button response, count number of responses for that particular button color
    # divide it by total number of responses to get percentage of bar
    percentage = []
    for i in range(numChoices):
        numResponses = responses.count(i)
        p = float(numResponses)/float(len(responses))
        percentage.append(p)

    # Loop through every block 2 response and see what percent of others
    # shared their response (i.e. append the percentage at index=this button response)
    # multiply value by 100 to get percent of others
    for response_index, response in enumerate(responses):
        dfWords.append(word)
        groundTruth.append(round(percentage[response]*100))
        if word in concrete:
            groundTruthCondition.append('concrete')
        else:
            groundTruthCondition.append('abstract')

# save to dataframe
dfGroundTruth = pd.DataFrame({'word':dfWords, 'groundTruth':groundTruth, 'condition':groundTruthCondition}, columns=['word', 'groundTruth', 'condition'])
# save df as csv
dfGroundTruth.to_csv("./experiment1/analysis3/ground-truth-by-condition.csv", index=False)

#-------------------------------------------------------------------------------
# CREATE CSV FOR EXPECTATION LOGISTIC REGRESSION

dfWords = []
aID1 = []
aID2 = []
match = []
aID1_expectation = []
for word_index, word in enumerate(sortedWords_entropy):
    # get aIDs
    aID = selectData(dfColor_block2, word, 'aID')

    buttonResponse = selectData(dfColor_block2, word, 'button_pressed')
    expectation = selectData(dfExpectation, word, 'sliderResponse')

    # loop over all the aIDs twice
    for id1_index, id1 in enumerate(aID):
        e = expectation[id1_index] # store the expectation rating for this aID1
        for id2_index, id2 in enumerate(aID):
            if id2 != id1: # only add rows for when person1 and person2 are NOT the same
                dfWords.append(word)
                aID1.append(id1)
                aID2.append(id2)
                aID1_expectation.append(e)
                # if the response for id1 is the same as id2
                if buttonResponse[id1_index] == buttonResponse[id2_index]:
                    match.append(1) # append 1 for True
                else:
                    match.append(0) # append 0 for False


# save to dataframe
dfRegression = pd.DataFrame({'word':dfWords, 'aID1':aID1, 'aID2':aID2, 'matchYN':match, 'aID1Expectation':aID1_expectation}, columns=['word', 'aID1', 'aID2', 'matchYN', 'aID1Expectation'])
# save df as csv
dfRegression.to_csv("./experiment1/analysis3/logistic-regression.csv", index=False)

#-------------------------------------------------------------------------------
# DELTA E (CIE2000): calculated off responses from block 2
# caution! takes a while to run

# avgDeltaE_block2 = getDeltaE(dfColor_block2)
# # sort words in order of ascending average DeltaE
# argsorted = np.argsort(avgDeltaE_block2)
# sortedWords = np.array(targetWords)[argsorted]
# sortedDeltaE_block2 = np.sort(avgDeltaE_block2)
#
# dfDeltaE = pd.DataFrame({'word':sortedWords, 'deltaE':sortedDeltaE_block2}, columns=['word', 'deltaE'])
# print(dfDeltaE)
# # save df as csv
# dfDeltaE.to_csv("./experiment1/analysis3/sorted-deltaE-block2.csv", index=False)
