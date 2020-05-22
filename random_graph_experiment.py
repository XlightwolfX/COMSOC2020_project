from socialnetwork import SocialNetwork
import argparse
import numpy as np
from tqdm import tqdm
from utils import regret, partial_regret
from collections import defaultdict
from votingrules import VotingRules
from dataset import Dataset
from networks import generate_graphs
import random
from scipy.stats import ttest_ind

# since every graph type has diff. parameter spaces,
# I have created this wrapper that returns a generator
# of parameters, given a graph type name.
def param_generator(graph_type):
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--alternatives', type=int, default=4, help='Number of alternatives.')
    parser.add_argument('--voters', type=int, default=100, help='Number of voters.')
    parser.add_argument('--voters_source', type=str, default='random', help='How to generate voters')
    parser.add_argument('--dataset_path', type=str, default='dataset/ED-00004-00000001.soc', help="If using preflib, which dataset?")
    parser.add_argument('--experiments', type=int, default=100, help='Number of experiments.')
    parser.add_argument('--graphs_per_setting', type=int, default=25, help='How many graphs to generate per param settings')
    parser.add_argument('--print_graph', action='store_true', help='Print the generated graph')
    parser.add_argument('--print_delegations', action='store_true', help='Print the delegation chains')
    parser.add_argument('--print_preferences', action='store_true', help='Print the preference counts')
    parser.add_argument('--skip_partial_regret', action='store_true', help='Don\'t use the alternative metric of partial regret instead.')    

    args = parser.parse_args()

    random.seed(args.seed)


    graph_types = ['path', 'random', 'regular', 'scale-free', 'small-world', 'caveman']
    paradigms = ['direct', 'proxy', 'liquid']

    # TODO: parametrize data source to use other means, for instance voter types.
    # TODO move this inside loop?
    if args.voters_source == 'random':
        data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
        true_preferences, true_counts = data.preferences, data.counts
    elif args.voters_source == 'preflib':
        data = Dataset(source=args.dataset_path)
        true_preferences, true_counts = data.preferences, data.counts
    elif args.voters_source == 'types':
        raise NotImplementedError('types experiment not implemented yet')
    else:
        raise NotImplementedError()

    # for regret, we need a three level structure: graph type, paradigm and rule.
    regrets = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : [])))
    if not args.skip_partial_regret:
        partial_regrets = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : [])))

    # this is used for the progress bar. First, we need to compute the total number
    # of graph types. Since diff. graph types have different settings, let's compute
    # their number explicitly
    COUNT_GRAPH_SETTINGS = 0
    for graph_type in graph_types:
        for param in param_generator(graph_type):
            COUNT_GRAPH_SETTINGS += 1

    # Now, total number of steps:
    TOT_EXPERIMENTS = COUNT_GRAPH_SETTINGS * args.graphs_per_setting * args.experiments * len(paradigms) * len(VotingRules.rules)

    # progress bar
    with tqdm(total=TOT_EXPERIMENTS) as pbar:

        # for all types of graphs
        for graph_type in graph_types:

            # for all parameters settings of this graph
            for params in param_generator(graph_type):

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
                                if not args.skip_partial_regret:
                                    partial_regrets[graph_type][paradigm][rule].append(partial_regret(winner, SN.id2voter.values()))

                                # update the progress bar
                                pbar.update(1)

    # TODO: visualize each different graph setting differently?

    # print result
    def print_results(data, name = 'regret'):
        # by default, we say it is not passed
        t_tests = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : 'FAILED'))))
        for graph_type in graph_types:
            for rule in VotingRules.rules:
                for paradigm in paradigms:
                    # data
                    regs = data[graph_type][paradigm][rule]
                    print(f'avg {name} {graph_type}, {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
                    # t test
                    for other in paradigms:
                        if other != paradigm:
                            data1 = data[graph_type][paradigm][rule]
                            data2 = data[graph_type][other][rule]
                            stat, p = ttest_ind(data1, data2)
                            if p <= 0.05:
                                t_tests[graph_type][paradigm][other][rule] = 'PASSED'
                print("#######")

        print("######### T-TESTS ###########")
        for graph_type in graph_types:
            for rule in VotingRules.rules:
                for paradigm in paradigms:
                    # basically, exclude one paradigm and look at the other two
                    # this is a quick way to generate all the combinations without repetition
                    others_two = list(set(paradigms) - {paradigm})
                    print(f"{graph_type}, {rule}, {others_two[0]}/{others_two[1]}: {t_tests[graph_type][others_two[0]][others_two[1]][rule]}")
            print('##')

        print("*********")



    print_results(regrets)
    if not args.skip_partial_regret:
        print_results(partial_regrets, name = 'partial regret')