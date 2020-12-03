import numpy as np
import scipy
import pandas as pd
from statistics import mean
from scipy.stats import entropy

#---------------------------------------------------------------------------------
# LOAD ALL COLOR PICKER DATA
df = pd.read_csv(r'../data/norming/colorPickerData-all.csv')
# select columns for word and RGB color response
cols = ["word", "button_pressed", "response_munsell", "condition"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block2_target_trial']
block = "both"

# LOAD ORDERED LIST OF WORDS BY ENTROPY
df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-%s.csv' % block)
df_entropy = df_entropy.rename(columns={block: "entropy"})

orderedWords = df_entropy['word'].to_list()
print(len(orderedWords))

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS

# function to select all responses that belong to a particular target word
def selectWordResponses(df, word):
    print(word)
    points = df[df['word'] == word]

    return points['button_pressed'].to_list()

def getProbabilities(df, orderedWords, numChoices):
    # initialize numWords (200) x numColors (88) array
    probabilities = np.empty([len(orderedWords), numChoices], dtype=float)

    for index, word in enumerate(orderedWords):
        # select all button responses that belong to a particular target word
        responses = np.array(selectWordResponses(df, word))

        pseudoCount = 1.0/len(responses)

        # count number of responses for each color for this word
        # remove 0's by adding psuedo counts of 1/numObservations
        # divide by number of choices to get probability
        probabilities[index,:] = [(np.count_nonzero(responses == i) + pseudoCount)/numChoices for i in range(numChoices)]

    return probabilities

# KL(P || Q) = sum x in X { P(x) * log(P(x) / Q(x) }
def computeKLDivergence(words, probabilities):
    divergences = np.empty([len(words), len(words)], dtype=float)
    # for each row (word) of the probabilities matrix, apply function
    for i in range(probabilities.shape[0]):
        thisWord = probabilities[i,:]
        for j in range(probabilities.shape[0]):
            otherWord = probabilities[j,:]

            divergences[i,j] = np.sum(thisWord*np.log2(thisWord/otherWord))

    return divergences

#---------------------------------------------------------------------------------
# COMPUTE DIVERGENCES
numChoices = 88

# select first half of ordered words (concrete) + their probabilities
    # -> compute KL divergence among words in that set
wordsCNC = orderedWords[:100]
probabilitiesCNC = getProbabilities(df, wordsCNC, numChoices) # get probabilities of each response for each word
divergencesCNC = computeKLDivergence(wordsCNC, probabilitiesCNC)

# select second half of ordered words (abstract) + their probabilities
    # -> compute KL divergence among words in that set
wordsABS = orderedWords[99:]
probabilitiesABS = getProbabilities(df, wordsABS, numChoices) # get probabilities of each response for each word
divergencesABS = computeKLDivergence(wordsABS, probabilitiesABS)

print(divergencesCNC.shape)
print(divergencesABS.shape)

#---------------------------------------------------------------------------------
# REJECTION SAMPLE WORDS BASED ON KL DIVERGENCE

# pick a set of 4 words
def sampleWords(words):
    contexts_list = []
    id = []
    for i in range(50):
        ctx = random.sample(words, 4)
        contexts_list.append(list(ctx))
        id.append(i)

    df = pd.DataFrame({'id':id, 'words':contexts_list})
    print(df)
    return df

# check the overlap of their response distributions (KL divergence),
# keep it if it's below some threshold, otherwise throw it away and pick another set.
