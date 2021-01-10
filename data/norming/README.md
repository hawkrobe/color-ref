We ran this experiment in five batches, each containing a set of 40 words seen 2 times by 100 participants.

* `create_word_sets.py` partitioned the data into these five sets (`norming-task-word-set-<i>.json`), which were balanced to have even numbers of 'abstract' and 'concrete' words.
* `rawData.zip` is a compressed file containing all the raw, anonymized data directly from Mechanical Turk.
* in `/analysis/experiment1.Rmd` we apply our exclusion criteria and pre-process this raw data and write it out as `colorPickerData.csv` for convenience in subsequent analyses
* `compiled-variance-entropy-glasgowRatings.csv` is created by python scripts in `/analysis/generate_contexts/`