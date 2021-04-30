# color-ref

Pre-registrations for both experiments can be found on [osf](https://osf.io/fcsyz/registrations)

## Reproducing experiments

Both experiments were designed to run online and require [`node.js`](https://nodejs.org/en/) to be installed.

* Experiment 1 can be run by navigating to `experiments/experiment1`, running `npm install` to install dependencies, then running `node app.js` to launch the experiment. Then go to `http://localhost:8887/word-color-priors.html` in your local browser. This experiment uses [jsPsych](https://www.jspsych.org).

* Experiment 2 can be run by following the same procedure in the `experiments/experiment2` subdirectory and then going to `http://localhost:8888/forms/consent.html` in two browser tabs (to play as both speaker and listener.)

## Reproducing analyses

To reproduce analyses, first unzip the raw data, which are stored in `./data/norming/` and `./data/data/refGame`. Then navigate to the analysis notebooks [`experiment1.Rmd`](https://github.com/hawkrobe/color-ref/blob/master/analyses/experiment1.Rmd) and [`experiment2.Rmd`](https://github.com/hawkrobe/color-ref/blob/master/analyses/experiment2.Rmd), respectively. 

