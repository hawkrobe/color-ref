import csv
import numpy as np
import colormath
import pandas as pd
import seaborn as sns
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, LCHabColor, SpectralColor, sRGBColor, XYZColor, LCHuvColor, IPTColor, HSVColor
#---------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import matplotlib

#---------------------------------------------------------------------------------
# INITIALIZE DATA
#---------------------------------------------------------------------------------

# LOAD ALL EXPECTATION RATING DATA
df_expectation = pd.read_csv(r'../data/norming/expectationData-all.csv')
# select columns for word and RGB color response
cols = ["word", "sliderResponse"]
df_expectation = df_expectation[cols]

# LOAD COLOR PICKER DATA FOR BLOCK 2 (EXPECTATION RESPONSES)
df_block2 = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
# select columns for word, button response, and condition (which block)
cols = ["word", "button_pressed", "condition"]
df_block2 = df_block2[cols]
# select all block2_target_trial rows
df_block2 = df_block2[df_block2['condition'] == 'block2_target_trial']

# LOAD ORDERED LIST OF WORDS BY ENTROPY for BLOCK 2 RESPONSES
df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-block2.csv')
words = df_entropy['word'].to_list()

#---------------------------------------------------------------------------------
# CREATE COLUMN FOR CONDITION

expectationCondition = []
concrete = words[:100]
abstract = words[-100:]

for index, row in df_expectation.iterrows():
    if row['word'] in concrete:
        expectationCondition.append('concrete')

    else:
        expectationCondition.append('abstract')

# add condition column to df
df_expectation['condition'] = expectationCondition
print(df_expectation)
df_expectation.to_csv("./expectation/expectations-by-condition.csv", index=False)

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS
#---------------------------------------------------------------------------------

# function to select all data of type type in df for word  that belong to a particular target word
def selectData(df, word, type):
    points = df[df['word'] == word]
    return points[type].to_list()

#---------------------------------------------------------------------------------
# COMPUTE GROUND TRUTH
#---------------------------------------------------------------------------------
dfWords = []
groundTruth = []
groundTruthCondition = []
# get percentages of response for each possible choice
for word_index, word in enumerate(words):
    numChoices = 88
    responses = selectData(df_block2, word, 'button_pressed')

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
df_groundTruth = pd.DataFrame({'word':dfWords, 'groundTruth':groundTruth, 'condition':groundTruthCondition}, columns=['word', 'groundTruth', 'condition'])
print(df_groundTruth)
# save df as csv
df_groundTruth.to_csv("./expectation/ground-truth-by-condition.csv", index=False)
