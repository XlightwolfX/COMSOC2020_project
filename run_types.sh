# # Train the agents.
for i in 2 4 6 8; do
    python3 number_types_experiment.py --voters_source types --experiments 100 --graphs_per_setting 100 --voter_types $i --voters 100
done
