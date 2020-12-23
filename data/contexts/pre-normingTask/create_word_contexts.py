import csv
import numpy as np
import colormath
import statistics
import gensim
import random
import math
import pandas as pd
from collections import defaultdict
from mpl_toolkits.mplot3d import axes3d, Axes3D
from statistics import mean 
#---------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import matplotlib
import seaborn as sns
#---------------------------------------------------------------------------------
# process the glasgow norms excel spreadsheet into pandas dataframe
df = pd.read_excel (r'GlasgowNorms.xlsx')
# impose familiarty threshold
threshold = 4.0
df = df.loc[df['FAM'] >= threshold]

#---------------------------------------------------------------------------------
# REMOVE UNWANTED WORDS

# rename first column header to WORD
df = df.rename(columns={df.columns[0]:'WORD'})
# offensive words, pop culture references, figures of speech, demographics, etc.
words_to_remove = ['indentify', 'grampa', 'ever', 'camp (effeminate)', 'hammered (drunk)', 'Apple (brand)', 'kiwi (New Zealander)', 'fuck (sex)', 'orgasm', 'erotic', 'sexy', 'sex (intercourse)', 'sexual', 'kinky', 'sex', 'screw (sex)', 'mate (copulate)', 'fuck (exclamation)', 'prick (dick)']
# find intersection of all words with words_to_remove
for w in words_to_remove:
    df = df[df['WORD'] != w]

#---------------------------------------------------------------------------------
# store desired columns of the dataframe as numpy arrays
words = df['WORD'].to_numpy()[1:]
imag = df['IMAG'].to_numpy()[1:]
cnc = df['CNC'].to_numpy()[1:]
fam = df['FAM'].to_numpy()[1:]

#---------------------------------------------------------------------------------
# SELECT WORDS

# sort words and imageability ratings by concreteness 
cnc_inds = cnc.argsort()
sorted_cnc = cnc[cnc_inds[::-1]]
sorted_imag = imag[cnc_inds[::-1]]
sorted_words = words[cnc_inds[::-1]]

# take top 2000 most concrete words and bottom 2000 least concrete (abstract) words + their corresponding imageability ratings
concrete_cnc = sorted_cnc[:500] #first 2000 items in array
abstract_cnc = sorted_cnc[-500:]  #last 2000 items in array
concrete_imag = sorted_imag[:500] 
abstract_imag = sorted_imag[-500:] 
concrete_words = sorted_words[:500] 
abstract_words = sorted_words[-500:]

# select 50 words from these sets for each group (abstract and concrete)
def selectWords(imag_ratings, filename, words, imag, cnc):
    final_words = []
    selected_words = open(filename, "w+")
    selected_words.write("familiarity threshold = %s\n" % (threshold))
    selected_words.write("\n")
    selected_words.write("WORD  IMAG  CNC  FAM\n")

    # return 50 evenly spaced numbers over the interval (i.e. min and max of imageability FOR EACH set of words)
    nums = np.around(np.linspace(min(imag_ratings), max(imag_ratings), num=100), 4)    

    for i, value in enumerate(nums): 
        # find imageability score closest to linspace values
        idx = (np.absolute(imag - value)).argmin()

        # add word to list
        final_words.append(words[idx])

        # write selected words and ratings to txt file 
        selected_words.write("%s:  " % (words[idx]))
        selected_words.write("%f  " % (imag[idx]))
        selected_words.write("%f  " % (cnc[idx]))
        selected_words.write("%f\n" % (fam[idx]))

        # set imageability score for that word to max value so the word doesn't get picked again
        imag[idx] = 10000

    selected_words.close()

    return final_words

# words need to be selected based off the sorted cnc ratings
final_cnc_words = selectWords(concrete_imag, "selected-cnc-group.txt", concrete_words, concrete_imag, concrete_cnc)
final_abs_words = selectWords(abstract_imag, "selected-abs-group.txt", abstract_words, abstract_imag, abstract_cnc)

# print(final_abs_words)
# print(final_cnc_words)

#---------------------------------------------------------------------------------
# CREATE CONTEXTS

# randomly sample groups of 4 words from each set

def createContexts(words, filename):
    contexts_list = []
    id = []
    contexts = open(filename, "w+")
    for i in range(50):
        ctx = random.sample(words, 4)
        contexts_list.append(list(ctx))
        id.append(i)
        contexts.write("%s  %s  %s  %s\n" % (ctx[0], ctx[1], ctx[2], ctx[3]))

    contexts.close()
    df = pd.DataFrame({'id':id, 'words':contexts_list})
    print(df)
    return df
    

df_cnc = createContexts(final_cnc_words, "concrete-contexts.txt")
# convert df to json
df_cnc.to_json('concrete-contexts.json', orient='records')  


df_abs = createContexts(final_abs_words, "abstract-contexts.txt")
# convert df to json
df_abs.to_json('abstract-contexts.json', orient='records')

#---------------------------------------------------------------------------------

