# COMSOC2020_project

Repository for a project of Computational Social Choice 2020 on UvA.

## Repo structure

* `dataset.py` Contains the facilities to process a preflib dataset, or in general, to contain a set of preference orders
* `networks.py` Contains the facilities to generate random graphs
* `utils.py` Contains the facilities to do various useful stuff

* `votingrules.py` Implements the voting rules
* `voter_types.py` Implements type-sampling

* `partialorders.py` Is a class representing a partial order
* `socialnetwork.py` Is a class representing a social net
* `voter.py` Is a class representing a voter

The rest is experiment scripts, described below

## Caveman Experiment

To run the caveman experiment, with the three settings discussed in the paper:

* `python caveman_experiment.py --indecisiveness 0 0 0 0.3 0.3 1` (IND1)
* `python caveman_experiment.py --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2)
* `python caveman_experiment.py --indecisiveness 1 1 1 0.3 0.3 0` (IND3)

We have normalized the indecision levels. For 4 alternatives, 0→1 strict order, 1→strict orders, etc...

## Types experiment

To run the types experiment, with the 9 three settings discussed in the paper:

* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 2 --voters 100 --indecisiveness 0 0 0 0.3 0.3 1` (IND1, 2 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 2 --voters 100 --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2, 2 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 2 --voters 100 --indecisiveness 1 1 1 0.3 0.3 0` (IND3, 2 types)

* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 4 --voters 100 --indecisiveness 0 0 0 0.3 0.3 1` (IND1, 4 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 4 --voters 100 --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2, 4 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 4 --voters 100 --indecisiveness 1 1 1 0.3 0.3 0` (IND3, 4 types)

* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 6 --voters 100 --indecisiveness 0 0 0 0.3 0.3 1` (IND1, 6 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 6 --voters 100 --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2, 6 types)
* `python number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voter_types 6 --voters 100 --indecisiveness 1 1 1 0.3 0.3 0` (IND3, 6 types)

We have normalized the indecision levels. For 4 alternatives, 0→1 strict order, 1→strict orders, etc...

To do the IMPARTIAL CULTURE experiment:

* `python random_graph_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voters 100 --indecisiveness 0 0 0 0.3 0.3 1` (IND1)
* `python random_graph_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voters 100 --indecisiveness 0 0.3 0.3 0.3 0.47 0.47 0.47 1 1 1` (IND2)
* `python random_graph_experiment.py --voters_source types --experiments 100 --graphs_per_setting 25 --voters 100 --indecisiveness 1 1 1 0.3 0.3 0` (IND3)