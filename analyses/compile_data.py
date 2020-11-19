import csv
import numpy as np
import pandas as pd
import gensim
from gensim.utils import lemmatize

#---------------------------------------------------------------------------------
# import all data files

# CHANGE CONDITION: both, block1, block2
block = 'block1'

# df_wordList = pd.read_excel(r'../data/norming/normingTask-final-word-list.xlsx')
df_glasgow = pd.read_excel(r'../data/contexts/GlasgowNorms.xlsx')
df_glasgow = df_glasgow.rename(columns={'Unnamed: 0': 'word'})
cols = ['word', 'IMAG', 'CNC', 'FAM']
df_glasgow = df_glasgow[cols]

df_variance = pd.read_csv(r'./variance/sorted-variances-all-%s.csv' % block)
df_variance = df_variance.rename(columns={block: "variance"})
words = df_variance['word'].to_list()

df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-%s.csv' % block)
df_entropy = df_entropy.rename(columns={block: "entropy"})

#---------------------------------------------------------------------------------
# attach correct values to correct word
entropies = []
imag = []
cnc = []
count = 0
original = []

for w in words:
    e = df_entropy['entropy'][df_entropy['word'] == w]
    entropies.append(e.tolist()[0])

    # handle known anomalies
    if w == 'bunkbed':
        i = df_glasgow['IMAG'][df_glasgow['word'] == 'bunk (bed)']
        imag.append(i.tolist()[0])
        c = df_glasgow['CNC'][df_glasgow['word'] == 'bunk (bed)']
        cnc.append(c.tolist()[0])
        original.append('Y')
    elif w == 'flag':
        print('%s not found' % w)
        imag.append("N/A")
        cnc.append("N/A")
        original.append('N/A')

    # base case: word exists in Glasgow set in its original form
    elif df_glasgow['word'].str.contains(w).any():
        i = df_glasgow['IMAG'][df_glasgow['word'] == w]
        imag.append(i.tolist()[0])
        c = df_glasgow['CNC'][df_glasgow['word'] == w]
        cnc.append(c.tolist()[0])
        original.append('Y')

    # # if the glagow set contains the lemmatized version of the word
    # # add it's rating but indicate 'N' for not original word
    # elif df_glasgow['word'].str.contains(lemmatize(w)).any():
    #     print(lemmatize(w))
    #     i = df_glasgow['IMAG'][df_glasgow['word'] == lemma]
    #     imag.append(i.tolist()[0])
    #     c = df_glasgow['CNC'][df_glasgow['word'] == lemma]
    #     cnc.append(c.tolist()[0])
    #     original.append('N')


    # else, not found at all
    else:
        count +=1
        imag.append("N/A")
        cnc.append("N/A")
        original.append('N/A')


print(count)
df_final = pd.DataFrame({'word':words, 'variance':df_variance['variance'], 'entropy':entropies, 'imageability':imag, 'concreteness':cnc})
cols = ['word', 'variance', 'entropy', 'imageability', 'concreteness']
df_final = df_final[cols]

# save df as csv
df_final.to_csv('../data/norming/compiled-variance-entropy-glasgowRatings.csv', index=False)
