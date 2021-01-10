# color-ref
Word-color associations

# ANALYSIS 1: variability measures vs. word ratings

### INPUT: 
colorPickerData-all.csv, GlasgowNorms.xlsx

### OUTPUTS:
entropy (both blocks' responses): ./experiment1/analysis1/sorted-variance-both.csv <br/> 
variance (both blocks' responses): ./experiment1/analysis1/sorted-entropy-both.csv <br/> 
delta E (block 1 responses only): ./experiment1/analysis1/sorted-deltaE-block1.csv <br/> 
compiled variability measures + word ratings: ./experiment1/analysis1/compiled-variabilityMeasures-glasgowRatings.csv

# ANALYSIS 2: intra-participant

### INPUT: 
colorPickerData-all.csv

### OUTPUT:
delta E (between responses from both blocks): ./experiment1/analysis2/block1-block2-deltaE.csv


# ANALYSIS 3: expectation

### INPUT: 
colorPickerData-all.csv, expectationData-all.csv

### OUTPUTS:
slider ratings by condition: ./experiment1/analysis3/expectation-by-condition.csv <br/> 
ground truth by condition (block 2 responses only): ./experiment1/analysis3/ground-truth-by-condition.csv <br/> 
logistic regression on participant match (block 2 responses only): ./experiment1/analysis3/logistic-regression.csv <br/> (^file too big to upload to GitHub) <br/> 
delta E (block 2 responses only): ./experiment1/analysis3/sorted-deltaE-block2.csv <br/> 