import numpy as np
import scipy
import pandas as pd
import random
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

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS

# function to select all responses that belong to a particular target word
def selectWordResponses(df, word):
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

# calculate kl divergence
# KL(P || Q) = sum x in X { P(x) * log(P(x) / Q(x) }
def kl_divergence(p, q):
    return np.sum(p * np.log2(p/q))

# calculate the js divergence
def js_divergence(p, q):
	m = 0.5 * (p + q)
	return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)

def computeDivergence(words, probabilities):
    divergence = np.empty([len(words), len(words)], dtype=float)
    # for each row (word) of the probabilities matrix, apply function
    for i in range(probabilities.shape[0]):
        p = probabilities[i,:]
        for j in range(probabilities.shape[0]):
            q = probabilities[j,:]

            divergence[i,j] = js_divergence(p, q)

    return divergence

#---------------------------------------------------------------------------------
# COMPUTE DIVERGENCES
numChoices = 88

# select first half of ordered words (concrete) + their probabilities
    # -> compute KL divergence among words in that set
wordsCNC = orderedWords[:100]
probabilitiesCNC = getProbabilities(df, wordsCNC, numChoices) # get probabilities of each response for each word
divergenceCNC = computeDivergence(wordsCNC, probabilitiesCNC)

# select second half of ordered words (abstract) + their probabilities
    # -> compute KL divergence among words in that set
wordsABS = orderedWords[99:]
probabilitiesABS = getProbabilities(df, wordsABS, numChoices) # get probabilities of each response for each word
divergenceABS = computeDivergence(wordsABS, probabilitiesABS)

# print(wordsCNC)
# print(divergenceCNC)
# print(divergenceABS)

np.savetxt("divergenceCNC.csv", divergenceCNC, delimiter=",")

#---------------------------------------------------------------------------------
# REJECTION SAMPLE WORDS BASED ON KL DIVERGENCE

def getDivergences(ctx):
    div = []
    # get divergence values for this sample
    for i in range(4):
        # get index of word i in orderedWords
        idx_i = orderedWords.index(ctx[i], 0, 100)
        for j in range(i+1, 4):
            # get index of word j in orderedWords
            idx_j = orderedWords.index(ctx[j], 0, 100)
            div.append(divergenceCNC[idx_i, idx_j]) # get divergence of word_i,j

    return div


# valid context = all divergences are above threshold
def validSample(div):
    return all(i >= 0.7 for i in div)

# pick sets of 4 from words
def sampleWords(ctx, div, words, contexts_list):
    # if there are only 4 words left, this must be a context
    if len(words) == 4:
        ctx = words
        contexts_list.append(list(ctx))
        return contexts_list

    if validSample(div):
        contexts_list.append(list(ctx)) # append to list of valid contexts
        modifiedWords = list(np.setdiff1d(np.array(words), ctx)) # remove these words from the set of words to sample from
        ctx = random.sample(modifiedWords, 4) # randomly sample the modified set
        div = getDivergences(ctx) # get the divergences for this context
        sampleWords(ctx, div, modifiedWords, contexts_list) # call sampleWords with modified set of words
    else:
        ctx = random.sample(words, 4) # resample from the same word set
        div = getDivergences(ctx) # get the divergences for this context
        sampleWords(ctx, div, words, contexts_list) # call sampleWords on same word set

def getContexts(wordSet, contexts_list):
    # get first context and divergences for this context
    ctx = np.random.choice(wordSet, 4)
    div = getDivergences(ctx)
    # call recursive function sampleWords to get contexts
    sampleWords(ctx, div, wordSet, contexts_list)

#--------------------------------

# iterate over word set twice and sample without replacement so that we
# get a set of contexts with each word used 2 times
concrete_contexts_list = []
# call getContexts 2x to get 50 contexts
getContexts(wordsCNC, concrete_contexts_list)
getContexts(wordsCNC, concrete_contexts_list)

abstract_contexts_list = []
# call getContexts 2x to get 50 contexts
getContexts(wordsCNC, abstract_contexts_list)
getContexts(wordsCNC, abstract_contexts_list)

# print(np.apply_along_axis(validSample, 1, abstract_contexts_list)) # check that all are valid samples
# print(concrete_contexts_list)
# print(abstract_contexts_list)

# id = list(range(50))
# df_cnc = pd.DataFrame({'id':id, 'words':concrete_contexts_list})
# df_cnc.to_json('concrete-contexts.json', orient='records')
#
# df_abs = pd.DataFrame({'id':id, 'words':abstract_contexts_list})
# df_abs.to_json('abstract-contexts.json', orient='records')
