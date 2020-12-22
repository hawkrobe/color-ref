import csv
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors


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

cols = ['imageability', 'variance', 'concreteness', 'entropy']
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce', axis=1)

ratio = var/entp
x = np.arange(0, ratio.shape[0])
c = ratio


# plt.scatter(x, ratio, c=c, s= 5)
#
# for i, txt in enumerate(words):
#     plt.annotate(txt, (x[i], ratio[i]), fontsize=6)
#
# plt.show()

# fig, ax = plt.subplots(tight_layout=True)
# hist = ax.hist2d(var, entp, bins=20)
# fig.colorbar(hist[3], ax=ax)
#
# plt.xlabel("Variance")
# plt.ylabel("Entropy")
# plt.savefig('./plots/entropy-variance-2d-histogram.png', bbox_inches='tight', dpi=300)
# plt.show()

# g = sns.relplot('entropy', 'variance', data=df, s=20, height=7, aspect=3)
# for i, txt in enumerate(words):
#     g.ax.text(entp[i], var[i], txt, fontsize=6)
#
# #plt.ylim(0,14)
# plt.show()
# # plt.savefig('./plots/imageability-vs-variance.png', bbox_inches='tight', dpi=300)


# g = sns.regplot('variance', 'entropy', data=df, ci=None)

# plt.show()

#---------------------------------------------------------------------------------
# plot concreteness vs. variance for df

# g = sns.relplot('concreteness', 'variance', data=df, s=20, height=7, aspect=3)
# for i, txt in enumerate(words):
#     g.ax.text(cnc[i], var[i], txt, fontsize=6)
#
# plt.show()
# plt.savefig('./plots/concreteness-vs-variance.png', bbox_inches='tight', dpi=300)

#---------------------------------------------------------------------------------
# plot all entropies

entp = pd.read_csv('./entropy/sorted-entropies-all-both.csv')

fig, ax = plt.subplots(figsize=(24, 4))
ax.tick_params(axis='x', labelsize=4)
ax.tick_params(axis='y', labelsize=8)
bar = sns.barplot(ax=ax, x="word", y="both", data=entp, hue='condition')
bar.set(xlabel=None, ylabel = "Entropy")
for item in bar.get_xticklabels():
    item.set_rotation(90)

plt.savefig('./plots/all-entropies.png', bbox_inches='tight', dpi=300)
# plt.show()
