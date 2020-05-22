from socialnetwork import SocialNetwork
import argparse
import numpy as np
from tqdm import tqdm
from utils import regret, partial_regret
from collections import defaultdict
from votingrules import VotingRules
from dataset import Dataset
from networks import generate_graphs
# ^ remove unused

# since every graph type has diff. parameter spaces,
# I have created this wrapper that returns a generator
# of parameters, given a graph type name.
def get_param_iterator(graph_type):
    degrees = [4, 8, 12, 16, 20, 24]
    probs = [0.25, 0.5, 0.75]
    clique_sizes = [10, 20, 50]

    if graph_type in ('path', 'scale-free'):
        return (dict() for _ in range(1))

    elif graph_type == 'random':
        return ({'prob': prob} for prob in probs)

    elif graph_type == 'regular':
        return ({'degree': degree} for degree in degrees)

    elif graph_type == 'small-world':
        return ({'degree': degree, 'prob': prob} for degree, prob in zip(degrees, probs))

    elif graph_type == 'caveman':
        return ({'clique_size': clique_size} for clique_size in clique_sizes)        

    else:
        raise NotImplementedError()

    return iter(param_iterator)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--alternatives', type=int, default=4, help='Number of alternatives.')
    parser.add_argument('--voters', type=int, default=100, help='Number of voters.')
    parser.add_argument('--experiments', type=int, default=100, help='Number of experiments.')
    parser.add_argument('--graphs_per_setting', type=int, default=25, help='How many graphs to generate per param settings')
    parser.add_argument('--print_graph', action='store_true', help='Print the generated graph')
    parser.add_argument('--print_delegations', action='store_true', help='Print the delegation chains')
    parser.add_argument('--print_preferences', action='store_true', help='Print the preference counts')
    parser.add_argument('--use_partial_regret', action='store_true', help='Use the alternative metric of partial regret instead.')

    args = parser.parse_args()

    graph_types = ['path', 'random', 'regular', 'scale-free', 'small-world', 'caveman']
    paradigms = ['direct', 'proxy', 'liquid']

    # TODO: parametrize data source to use other means, for instance voter types.
    data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
    true_preferences, true_counts = data.preferences, data.counts

    # for regret, we need a three level structure: graph type, paradigm and rule.
    regrets = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : [])))
    if args.use_partial_regret:
        partial_regrets = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : [])))

    # this is used for the progress bar. First, we need to compute the total number
    # of graph types. Since diff. graph types have different settings, let's compute
    # their number explicitly
    COUNT_GRAPH_SETTINGS = 0
    for graph_type in graph_types:
        for param in get_param_iterator(graph_type):
            COUNT_GRAPH_SETTINGS += 1

    # Now, total number of steps:
    TOT_EXPERIMENTS = COUNT_GRAPH_SETTINGS * args.graphs_per_setting * args.experiments * len(paradigms) * len(VotingRules.rules)

    # progress bar
    with tqdm(total=TOT_EXPERIMENTS) as pbar:

        # for all types of graphs
        for graph_type in graph_types:

            # for all parameters settings of this graph
            for params in get_param_iterator(graph_type):

                # generate some graphs with this parameters
                graph_generator = generate_graphs(num_voters=data.count_voters(), \
                    num_graphs=args.graphs_per_setting, gtype=graph_type, seed = args.seed, params = params)

                # for every graph
                for graph in graph_generator:

                    # get the corresponding SN
                    SN = SocialNetwork(strategy = 'dataset_and_nx_graph', graph = graph, dataset = data)
                    # and compare it under every paradigm
                    for paradigm in paradigms:

                        # for more than one experiment
                        for _ in range(args.experiments):
                            # get the preferences
                            SN_preferences, SN_counts = SN.get_preferences(paradigm,\
                                print_delegations = args.print_delegations, print_preferences = args.print_preferences)

                            # and get the winner for every rule
                            for rule in VotingRules.rules:
                                winner = VotingRules.elect(rule, SN_preferences, SN_counts, tiebreaking = min)

                                regrets[graph_type][paradigm][rule].append(regret(winner, true_preferences, true_counts))
                                if args.use_partial_regret:
                                    partial_regrets[graph_type][paradigm][rule].append(partial_regret(winner, SN.id2voter.values()))

                                # update the progress bar
                                pbar.update(1)

    # TODO: visualize each different graph setting differently?

    # print result
    for graph_type in graph_types:
        for rule in VotingRules.rules:
            for paradigm in paradigms:
                regs = regrets[graph_type][paradigm][rule]
                print(f'avg regret of {graph_type}, {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
                if args.use_partial_regret:
                    regs = regrets[graph_type][paradigm][rule]
                    print(f'avg partial regret of {graph_type}, {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
        print("#######")