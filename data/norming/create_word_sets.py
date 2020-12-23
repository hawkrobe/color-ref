import numpy as np
import statistics
import random
import math
import pandas as pd
#---------------------------------------------------------------------------------
# load in each set of words
df_cnc = pd.read_excel (r'TO EDIT_ final experiment word list.xlsx', sheet_name=0)
df_abs = pd.read_excel (r'TO EDIT_ final experiment word list.xlsx', sheet_name=1)

abstract_set = df_abs['REPLACEMENT'].to_numpy()
concrete_set = df_cnc['REPLACEMENT'].to_numpy()

# shuffle words
np.random.shuffle(abstract_set)
np.random.shuffle(concrete_set)

# for converting to json format
ids = np.arange(40)


# print(abstract_set)
# print(concrete_set)


start = 0
end = 20
for i in range(5):
    # pick subset of 20 abstract words
    abs_subset = abstract_set[start+i*20:end+i*20]
    # pick subset of 20 concrete words
    cnc_subset = concrete_set[start+i*20:end+i*20]
    # combine subsets of 20 concrete and 20 abstract into set of 40
    subset = np.concatenate([abs_subset, cnc_subset])
    # shuffle 40-word subsets to create final subsets
    np.random.shuffle(subset)
    print(subset)

    # save as json
    df_subset = pd.DataFrame({'id':ids, 'word':subset})
    df_subset.to_json('norming-task-word-set-%d.json' % i, orient='records')
