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
# CHANGE CONDITION: both, block1, block2
block = 'both'

df_variance = pd.read_csv(r'../../analyses/variance/sorted-variances-all-%s.csv' % block)
df_variance = df_variance.rename(columns={block: "variance"})
words_var = df_variance['word'].to_list()

df_entropy = pd.read_csv(r'../../analyses/entropy/sorted-entropies-all-%s.csv' % block)
df_entropy = df_entropy.rename(columns={block: "entropy"})
words_entp = df_entropy['word'].to_list()

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

final_cnc_words = words_entp[0:100]
df_cnc = createContexts(final_cnc_words, "concrete-contexts.txt")
# convert df to json
df_cnc.to_json('concrete-contexts.json', orient='records')

final_abs_words = words_entp[100:]
df_abs = createContexts(final_abs_words, "abstract-contexts.txt")
# convert df to json
df_abs.to_json('abstract-contexts.json', orient='records')

#---------------------------------------------------------------------------------
