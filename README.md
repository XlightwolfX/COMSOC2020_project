# COMSOC2020_project

Repository for a project of Computational Social Choice 2020 on UvA.

## Repo structure

* `dataset.py` Contains the facilities to process a preflib dataset, or in general, to contain a set of preference orders
* `networks.py` Contains the facilities to generate random graphs
* `utils.py` Contains the facilities to do various useful stuff

* `votingrules.py` Implements the voting rules

* `partialorders.py` Is a class representing a partial order
* `socialnetwork.py` Is a class representing a social net
* `voter.py` Is a class representing a voter

The rest is experiment scripts, described below

## Caveman Experiment

To run the caveman experiment, with the three settings discussed in the paper:

`python caveman_experiment.py --indecisiveness 0 0 0 0.3 0.3 1` (IND1)
`python caveman_experiment.py --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2)
`python caveman_experiment.py --indecisiveness 1 1 1 0.3 0.3 0` (IND3)

We have normalized the indecision levels. For 4 alternatives, 0→1 strict order, 1→strict orders, etc...

## Types experiment

...Zi Long, Write Here!...