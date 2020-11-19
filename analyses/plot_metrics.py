import csv
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


#---------------------------------------------------------------------------------
df = pd.read_csv('../data/norming/compiled-variance-entropy-glasgowRatings.csv')
# print(df)

words = df['word'].to_numpy()
imag = df['imageability'].to_numpy()
cnc = df['concreteness'].to_numpy()
var = df['variance'].to_numpy()
entp = df['entropy'].to_numpy()
#---------------------------------------------------------------------------------
# plot imageability vs. variance for df

cols = ['imageability', 'variance', 'concreteness']
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce', axis=1)

g = sns.relplot('imageability', 'variance', data=df, s=20, height=7, aspect=3)
for i, txt in enumerate(words):
    g.ax.text(imag[i], var[i], txt, fontsize=6)

plt.show()
# plt.savefig('./plots/imageability-vs-variance.png', bbox_inches='tight', dpi=300)

#---------------------------------------------------------------------------------
# plot concreteness vs. variance for df

g = sns.relplot('concreteness', 'variance', data=df, s=20, height=7, aspect=3)
for i, txt in enumerate(words):
    g.ax.text(cnc[i], var[i], txt, fontsize=6)

plt.show()
# plt.savefig('./plots/concreteness-vs-variance.png', bbox_inches='tight', dpi=300)
