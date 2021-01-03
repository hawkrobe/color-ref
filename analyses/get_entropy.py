import numpy as np
import scipy
import pandas as pd
from statistics import mean
from scipy.stats import entropy

# https://tdhopper.com/blog/entropy-of-a-discrete-probability-distribution
# #---------------------------------------------------------------------------------
# STEP 0: make points x LAB array of dummy points

df = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
# select columns for word and RGB color response
cols = ["word", "button_pressed", "response_munsell", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block2_target_trial']
block = "both"

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
counts = np.empty([len(targetWords), numChoices], dtype=float)
probabilities = np.empty([len(targetWords), numChoices], dtype=float)
entropies = np.empty([len(targetWords),])

for index, word in enumerate(targetWords):
    responses = np.array(selectWordResponses(df, word))

    pseudoCount = 1/numChoices

    # count number of responses for each color for this word by adding
    # psuedo counts of 1/numChoices to every cell
    counts[index,:] = [(np.count_nonzero(responses == i) + pseudoCount) for i in range(numChoices)]

# normalize by dividing by total updated counts for that word
for index, word in enumerate(targetWords):
    probabilities[index,:] = counts[index,:]/np.sum(counts[index,:])

    # calculate entropy
    entropies[index] = scipy.stats.entropy(probabilities[index,:], base=2)

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
df2.to_csv("./entropy/sorted-entropies-all-%s-88.csv" % block, index=False)
