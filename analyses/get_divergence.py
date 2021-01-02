import numpy as np
import scipy
import pandas as pd
import random
from statistics import mean
from scipy.stats import entropy

#---------------------------------------------------------------------------------
# INITIALIZE DATA
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
# COMPUTING DIVERGENCE: HELPER FUNCTIONS
#---------------------------------------------------------------------------------
# function to select all responses that belong to a particular target word
def selectWordResponses(df, word):
    points = df[df['word'] == word]

    return points['button_pressed'].to_list()

def getProbabilities(df, orderedWords, numChoices):
    # initialize numWords (200) x numColors (88) array
    counts = np.empty([len(orderedWords), numChoices], dtype=float)
    probabilities = np.empty([len(orderedWords), numChoices], dtype=float)

    for index, word in enumerate(orderedWords):
        # select all button responses that belong to a particular target word
        responses = np.array(selectWordResponses(df, word))

        pseudoCount = 1.0/numChoices

        # count number of responses for each color for this word by adding
        # psuedo counts of 1/numChoices to every cell
        counts[index,:] = [(np.count_nonzero(responses == i) + pseudoCount) for i in range(numChoices)]

        # normalize by dividing by total updated counts for that word
    for index, word in enumerate(orderedWords):
        probabilities[index,:] = counts[index,:]/np.sum(counts[index,:])

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

#--------------------------------
# COMPUTE DIVERGENCES
#--------------------------------
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

# # COMPUTE DIVERGENCE ON ALL WORDS FOR FUTURE SIMPLICITY
# probabilities = getProbabilities(df, orderedWords, numChoices) # get probabilities of each response for each word
# divergences = computeDivergence(orderedWords, probabilities)
# print(probabilities.shape)
# print(divergences.shape)

# np.savetxt("divergences.csv", divergences, delimiter=",")


#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# REJECTION SAMPLE WORDS BASED ON KL DIVERGENCE: HELPER FUNCTIONS
#---------------------------------------------------------------------------------

# NOTE: CHANGE THE wordsXXX and divergenceXXX variables to appropriate set !!!
def getDivergences(ctx):
    div = []
    # get divergence values for this sample
    for i in range(4):
        # get index of word i in orderedWords
        idx_i = wordsABS.index(ctx[i])
        for j in range(i+1, 4):
            # get index of word j in orderedWords
            idx_j = wordsABS.index(ctx[j])
            div.append(divergenceABS[idx_i, idx_j]) # get divergence of word_i,j

    return div


# valid context = all divergences are above threshold
def validSample(div, threshold):
    return all(i >= threshold for i in div)

# pick sets of 4 from words
def sampleWords(ctx, div, words, contexts_list, threshold):
    # if there are only 4 words left, this must be a context
    if len(words) == 4:
        ctx = words
        contexts_list.append(list(ctx))
        return contexts_list

    if validSample(div, threshold):
        contexts_list.append(list(ctx)) # append to list of valid contexts
        modifiedWords = list(np.setdiff1d(np.array(words), ctx)) # remove these words from the set of words to sample from
        ctx = random.sample(modifiedWords, 4) # randomly sample the modified set
        div = getDivergences(ctx) # get the divergences for this context
        sampleWords(ctx, div, modifiedWords, contexts_list, threshold) # call sampleWords with modified set of words
    else:
        ctx = random.sample(words, 4) # resample from the same word set
        div = getDivergences(ctx) # get the divergences for this context
        sampleWords(ctx, div, words, contexts_list, threshold) # call sampleWords on same word set

def getContexts(wordSet, contexts_list, threshold):
    # get first context and divergences for this context
    ctx = np.random.choice(wordSet, 4)
    div = getDivergences(ctx)
    # call recursive function sampleWords to get contexts
    sampleWords(ctx, div, wordSet, contexts_list, threshold)


#--------------------------------
# iterate over word set twice and sample without replacement so that we
# get a set of contexts with each word used 2 times

# id = list(range(50))
# thresholdCNC = 0.7
# thresholdABS = 0.3

#--------------------------------
# MAKE CONCRETE CONTEXTS
#--------------------------------
# concrete_contexts_list = []
# # call getContexts 2x to get 50 contexts
# getContexts(wordsCNC, concrete_contexts_list, thresholdCNC)
# getContexts(wordsCNC, concrete_contexts_list, thresholdCNC)
# print(concrete_contexts_list)
# df_cnc = pd.DataFrame({'id':id, 'words':concrete_contexts_list})
# df_cnc.to_json('../data/contexts/divergence-rejection-sampling/concrete-contexts.json', orient='records')

#--------------------------------
# MAKE ABSTRACT CONTEXTS
#--------------------------------
# abstract_contexts_list = []
# # call getContexts 2x to get 50 contexts
# getContexts(wordsABS, abstract_contexts_list, thresholdABS)
# getContexts(wordsABS, abstract_contexts_list, thresholdABS)
# print(abstract_contexts_list)
# df_abs = pd.DataFrame({'id':id, 'words':abstract_contexts_list})
# df_abs.to_json('../data/contexts/divergence-rejection-sampling/abstract-contexts.json', orient='records')


#---------------------------------------------------------------------------------
# MAKE CSV WITH ALL PAIRWISE DIVERGENCES
#---------------------------------------------------------------------------------

# compute divergence on all words
probabilities = getProbabilities(df, orderedWords, numChoices) # get probabilities of each response for each word
divergences = computeDivergence(orderedWords, probabilities)
# print(probabilities)
# print(np.sum(probabilities, axis=1))
# print(divergences)
#
# # check if matrix is symmetric
# if np.allclose(divergences, divergences.T, rtol=1e-05, atol=1e-08):
#     print("divergence matrix is symmetric")
# else:
#     print("divergence matrix is NOT symmetric")

# # make a csv with all pairwise overlaps
# word1 = []
# word2 = []
# divergenceList = []
# for i, firstWord in enumerate(orderedWords):
#     word1.extend([firstWord]*len(orderedWords))
#     divergenceList.extend(divergences[i,:].tolist())
#     for j, secondWord in enumerate(orderedWords):
#         word2.append(secondWord)
#
# df_output = pd.DataFrame({'word1':word1, 'word2': word2, 'JSdivergence':divergenceList}, columns=['word1', 'word2', 'JSdivergence'])
# df_output.to_csv("./divergence/KL-divergence-%s.csv" % block, index=False)

#---------------------------------------------------------------------------------
# RADIUS SAMPLING ALGORITHM: 1ST SET OF 50 CONTEXTS
#---------------------------------------------------------------------------------
# get symmetric matrix of divergences for this context
# lower divergence = identical, higher divergence = different
def getDivergences(ctx):
    div = np.empty([4,4])
    # get divergence values for this sample
    for i in range(4):
        # get index of word i in orderedWords
        idx_i = orderedWords.index(ctx[i])
        for j in range(4):
            # get index of word j in orderedWords
            idx_j = orderedWords.index(ctx[j])
            div[i,j] = divergences[idx_i, idx_j] # get divergence of word_i,j

    return div

def getOverlappingPairs(div, threshold):
    div = np.triu(div) # keep upper triangle of symmatrix
    return np.argwhere((div <= threshold) & (div > 0.0)) # find pairs that are not 0, but below threshold

def getWordEntropy(df, word):
    points = df[df['word'] == word]

    return points['entropy']

# pick sets of 4 from words
def radiusSampleWords(ctx, words, visited, contexts_list, threshold):
    # if there are only 3 words left, this must be a context
    if len(contexts_list) == 49:
        ctx.append(random.sample(list(np.setdiff1d(np.array(orderedWords[-20:]), ctx)), 1)[0])
        contexts_list.append(ctx)
        return

    # 3) if any pair of words has overlap > threshold
    # keep the one with smaller entropy and replace the other one with the next word in the list (i.e. 'apple')
    div = getDivergences(ctx)
    overlaps = getOverlappingPairs(div, threshold) # get indices of pairs that are below threshold

    # if there are no overlapping pairs for this context
    if overlaps.size == 0:
        contexts_list.append(ctx) # append to list of valid contexts
        updatedWords = filter(lambda x: x not in ctx, words) # update word list having removed the words in the valid context
        visited = [] # set visited to empty
        ctx = updatedWords[:4] # set new context = first 4 words of updated word list
        return radiusSampleWords(ctx, updatedWords, visited, contexts_list, threshold) # call sampleWords with modified set of words

    else:
        for pair in overlaps:
            # indices of words in pair in context
            idx0 = pair[0]
            idx1 = pair[1]
            visited.extend(ctx)
            # create temp list of words to consider without words that have been visited
            temp = filter(lambda x: x not in visited, words)

            # if temp is empty and there are no more words to consider, just accept this context and return from this recursive call
            if len(temp) == 0:
                contexts_list.append(ctx) # append to list of valid contexts
                updatedWords = filter(lambda x: x not in ctx, words) # update word list having removed the words in the valid context
                visited = [] # set visited to empty
                ctx = updatedWords[:4] # set new context = first 4 words of updated word list

                return radiusSampleWords(ctx, updatedWords, visited, contexts_list, threshold) # call sampleWords with modified set of words


            # make new context without the the word at index 1 of pair
            # (because the contexts are ordered, word @ index 0 must be lower entropy than word @ index 1)
            # append first word in word list that was not in ctx
            else:
                newCtx = filter(lambda x: x != ctx[idx1], ctx)
                newCtx = newCtx + [temp[0]]
                return radiusSampleWords(newCtx, words, visited, contexts_list, threshold) # call sampleWords on actual word set

#---------------------------------------------------------------------------------

words = orderedWords

# 1) initialize with first four words (i.e. lemon, sun, tomato, fire)
ctx = words[:4]
div = getDivergences(ctx)
contexts_list = []
visited = []

# call recursive function sampleWords to get contexts with threshold of overlap = 0.25
radiusSampleWords(ctx, words, visited, contexts_list, 0.3)
print("first set of contexts:")
print(contexts_list)
print(" ")


id = list(range(50))
df_output = pd.DataFrame({'id':id, 'words':contexts_list})
# print(df_output)
# df_output.to_json('../data/contexts/radius-sampling/contexts-set1.json', orient='records')


#---------------------------------------------------------------------------------
# RADIUS SAMPLING ALGORITHM: SECOND SET OF 50 CONTEXTS
#---------------------------------------------------------------------------------

# check if thisWord was in a context with the other words in ctx
def wereTogetherBefore(ctx, thisWord):
    potentialCtx = ctx + [thisWord]
    for index, oldCtx in enumerate(oldContexts):
        for c in ctx:
            if (c in oldCtx) and (thisWord in oldCtx):
                return True

def isOverlap(ctx, thisWord, threshold):
    # get index of thisWord in orderedWords
    idx_i = orderedWords.index(thisWord)
    for j in range(len(ctx)):
        # get index of word j in orderedWords
        idx_j = orderedWords.index(ctx[j])
        if divergences[idx_i, idx_j] < threshold:
            return True

def sampleSecondSet(ctx, words, visited, contexts_list2, threshold):
    if len(words) < 4:
        return

    if len(contexts_list) == 49:
        ctx.append(random.sample(list(np.setdiff1d(np.array(orderedWords[-20:]), ctx)), 1)[0])
        contexts_list2.append(ctx)
        return

    if len(ctx) == 4:
        contexts_list2.append(ctx) # append to list of valid contexts
        updatedWords = filter(lambda x: x not in ctx, words) # update word list having removed the words in the valid context
        visited = [] # set visited to empty
        if len(updatedWords) == 0:
            return
        else:
            ctx = [updatedWords[0]] # set new context = next available word
            return sampleSecondSet(ctx, updatedWords, visited, contexts_list2, threshold) # call sampleSecondSet with modified set of words

    else:
        visited.extend(ctx)
        # create temp list of words to consider without words that have been visited
        temp = filter(lambda x: x not in visited, words)

        # if temp is empty and there are no more words to consider, just accept this context and return from this recursive call
        if len(temp) == 0:
            contexts_list2.append(ctx) # append to list of valid contexts
            threshold = 0.1
            updatedWords = filter(lambda x: x not in ctx, words) # update word list having removed the words in the valid context
            visited = [] # set visited to empty
            ctx = [updatedWords[0]] # set new context = next available word

            return sampleSecondSet(ctx, updatedWords, visited, contexts_list2, threshold)

        else:
            w = temp[0]

            # if this word was NOT already with any of the words in this context AND
            # its overlap with any of the words is NOT below the threshold
            if (not wereTogetherBefore(ctx, w)) and (not isOverlap(ctx, w, threshold)):
                # add it to this context
                newCtx = ctx + [w]
                return sampleSecondSet(newCtx, words, visited, contexts_list2, threshold) # call sampleSecondSet on actual word set

            else:
                # add w to visited
                visited.append(w)
                # call sampleSecondSet with new visited
                return sampleSecondSet(ctx, words, visited, contexts_list2, threshold) # call sampleWords on actual word set


#---------------------------------------------------------------------------------
import itertools
# flatten old contexts into new word list, except for last element which was a duplicate to get 200 words
lastWordOfPreviousSet = list(itertools.chain.from_iterable(contexts_list))[-1]
words = list(itertools.chain.from_iterable(contexts_list))[:-1]
oldContexts = contexts_list
threshold = 0.3

# initialize context with first word
ctx = [words[0]]
visited = []
contexts_list2 = []

sampleSecondSet(ctx, words, visited, contexts_list2, 0.3)
print("second set of contexts:")
print(contexts_list2)
print("-- number of contexts in second set = %d" % len(contexts_list2))
print(" ")

# because we only had 199 unique words, append another word to the end of the context with 3 words from the last 20 words according to entropy
# make sure that the word that is appended was not also used twice in the previou set of 50 contexts (aka the very last word of that set)
for ctx2 in contexts_list2:
    if len(ctx2) == 3:
        exclude = ctx2 + [lastWordOfPreviousSet]
        ctx2.append(random.sample(list(np.setdiff1d(np.array(orderedWords[-20:]), exclude)), 1)[0])

# SAVE SECOND SET OF CONTEXTS
id = list(range(50))
df_output = pd.DataFrame({'id':id, 'words':contexts_list2})
df_output.to_json('../data/contexts/radius-sampling/contexts-set2.json', orient='records')


#---------------------------------------------------------------------------------
# SANITY CHECKS

print("CROSS CHECKING CONTEXTS IN SECOND SET:")

# check for duplicate contexts
duplicates = False
for ctx1 in contexts_list:
    for ctx2 in contexts_list2:
        if ctx1 == ctx2:
            duplicates = True

if duplicates:
    print("-- duplicates found")
else:
    print("-- no duplicates found")

print(" ")

# check how many contexts have divergences less than 0.3
count = 0

for ctx2 in contexts_list2:
    div2 = getDivergences(ctx2)
    overlaps = getOverlappingPairs(div2, threshold) # get indices of pairs that are below threshold

    # if there are no overlapping pairs for this context
    if overlaps.size != 0:
        count += 1
        print(ctx2)
        print(div2)

print("-- %d contexts in the second set have divergences less than %s" % (count, threshold))
print(" ")

for ctx2 in contexts_list2:
    if len(ctx2) < 4:
        print(ctx2)
        print("has less than 4 words")

numWordsInSecondSet = len(set(itertools.chain.from_iterable(contexts_list2)))
print("-- second set has %s unique words" % numWordsInSecondSet)

#---------------------------------------------------------------------------------
# SAVE ALL CONTEXTS
allIds = list(range(100))
contexts_list.extend(contexts_list2)
allContexts = contexts_list
df_finaloutput = pd.DataFrame({'id':allIds, 'words':allContexts})
df_finaloutput.to_json('../data/contexts/radius-sampling/contexts-all.json', orient='records')
