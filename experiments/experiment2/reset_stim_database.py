import pymongo as pm
import pandas as pd
import json

# this auth.json file contains credentials
with open('auth.json') as f :
    auth = json.load(f)

user = auth['user']
pswd = auth['password']

# initialize mongo connection
conn = pm.MongoClient('mongodb://{}:{}@127.0.0.1'.format(user, pswd))

# get database for this project
db = conn['color-ref']

# get stimuli collection from this database
print('possible collections include: ', db.collection_names())
stim_coll = db['context-stims']

# empty stimuli collection if already exists
# (note this destroys records of previous games)
if stim_coll.count() != 0 :
    stim_coll.drop()

# Loop through evidence and insert into collection
concrete_sets = pd.read_json('../../data/contexts/radius-sampling/concrete-contexts.json',
                             'records')
abstract_sets = pd.read_json('../../data/contexts/radius-sampling/abstract-contexts.json',
                             'records')

for row_i, row in concrete_sets.sample(frac=1).iterrows() :
    packet = {
        'words' : row.words,
        'id' : row.id,
        'condition' : 'concrete',
        'numGames': 0,
        'games' : []
    }
    stim_coll.insert_one(packet)

for row_i, row in abstract_sets.sample(frac=1).iterrows() :
    packet = {
        'words' : row.words,
        'id' : row.id,
        'condition' : 'abstract',
        'numGames': 0,
        'games' : []
    }
    stim_coll.insert_one(packet)

print('checking one of the docs in the collection...')
print(stim_coll.find_one())
