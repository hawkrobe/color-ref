We ran this experiment in five batches, each containing a set of 40 words seen 2 times by 100 participants.

* `create_word_sets.py` partitioned the data into these five sets (`norming-task-word-set-<i>.json`), which were balanced to have even numbers of 'abstract' and 'concrete' words.
* `dataFromMongo.csv.zip` is a compressed file containing raw data directly from Mechanical Turk.
* in `/analysis/experiment1.Rmd` we then apply exclusion criteria and pre-process this raw data and write it out as `colorPickerData-0.csv` for subsequent analyses
* `compiled-variance-entropy-glasgowRatings.csv` is created by python scripts in `/analysis/generate_contexts/`