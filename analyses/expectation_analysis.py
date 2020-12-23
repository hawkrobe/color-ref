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

# LOAD ALL COLOR PICKER DATA
df = pd.read_csv(r'../data/norming/expectationData-all.csv')
# select columns for word and RGB color response
cols = ["word", "sliderResponse"]
df = df[cols]

# CHANGE CONDITION TO SELECT DIFFERENT BLOCK
# df = df[df['condition'] == 'block1_target_trial']
block = "both"

# LOAD ORDERED LIST OF WORDS BY ENTROPY
df_entropy = pd.read_csv(r'./entropy/sorted-entropies-all-%s.csv' % block)
df_entropy = df_entropy.rename(columns={block: "entropy"})
words = df_entropy['word'].to_list()

# LOAD VARIANCES
df_var = pd.read_csv(r'./variance/sorted-variances-all-%s.csv' % block)
df_var = df_var.rename(columns={block: "variacne"})

#---------------------------------------------------------------------------------
# HELPER FUNCTIONS
#---------------------------------------------------------------------------------

# function to select all RGB points that belong to a particular target words
def selectPoints(df, word):
    points = df[df['word'] == word]
    return points['sliderResponse'].to_list()


#---------------------------------------------------------------------------------
# COMPUTE AVG EXPECTATION
#---------------------------------------------------------------------------------

ratings = []
condition = []
concrete = words[:100]
abstract = words[-100:]

for index, row in df.iterrows():
    if row['word'] in concrete:
        condition.append('concrete')

    else:
        condition.append('abstract')

# add condition column to df
df['condition'] = condition
print(df)

df.to_csv("./expectation/expectations-by-condition.csv", index=False)
