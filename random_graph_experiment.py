from socialnetwork import SocialNetwork
import argparse
import numpy as np
from tqdm import tqdm
from utils import regret, partial_regret, ind_levels
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
    degrees = [4, 8, 12, 16]
    probs = [0.25, 0.5, 0.75]

    if graph_type in ('path', 'scale-free'):
        return (dict() for _ in range(1))

    elif graph_type == 'random':
        return ({'prob': prob} for prob in probs)

    elif graph_type == 'regular':
        return ({'degree': degree} for degree in degrees)

    elif graph_type == 'small-world':
        def param_generator():
            for degree in degrees:
                for prob in probs:
                    yield {'degree': degree, 'prob': prob}

        return param_generator()

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
    parser.add_argument('--voter_types', type=int, default=2, help='Number of types for \'types\' source')
    parser.add_argument('--type_gen', type=str, default='half_normal', help='distribution for \'types\' source [half_normal|tshirt]')
    parser.add_argument('--print_graph', action='store_true', help='Print the generated graph')
    parser.add_argument('--print_delegations', action='store_true', help='Print the delegation chains')
    parser.add_argument('--print_preferences', action='store_true', help='Print the preference counts')
    parser.add_argument('--skip_print_winners', action='store_true', help='Skip the printing of the winner counts')
    parser.add_argument('--partial_regret', action='store_true', help='Use also the alternative metric of partial regret.')
    parser.add_argument('--ttest', action='store_true', help='Perform t-test')

    args = parser.parse_args()

    random.seed(args.seed)

    graph_types = ['path', 'random', 'regular', 'scale-free', 'small-world']
    paradigms = ['direct', 'proxy', 'liquid']

    # TODO move this inside loop?
    # if args.voters_source == 'random':
    #     data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
    #     true_preferences, true_counts = data.preferences, data.counts
    # elif args.voters_source == 'preflib':
    #     data = Dataset(source=args.dataset_path)
    #     true_preferences, true_counts = data.preferences, data.counts
    # elif args.voters_source == 'types':
    #     data = Dataset(source='type_random', rand_params=[args.alternatives, args.voters, args.voter_types],
    #                    type_generation=args.type_gen)
    #     true_preferences, true_counts = data.preferences, data.counts
    # else:
    #     raise NotImplementedError('Unknown voter source')

    # for regret, we need a three level structure: graph type, paradigm and rule.
    regrets = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : [])))
    winners = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : 0))))
    if args.partial_regret:
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

    possible_indecision_levels = ind_levels(args.alternatives)

    # progress bar
    with tqdm(total=TOT_EXPERIMENTS) as pbar:
        if args.voters_source == 'random':
            data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
            true_preferences, true_counts = data.preferences, data.counts
        elif args.voters_source == 'preflib':
            data = Dataset(source=args.dataset_path)
            true_preferences, true_counts = data.preferences, data.counts
        elif args.voters_source == 'types':
            data = Dataset(source='type_random', rand_params=[args.alternatives, args.voters, args.voter_types],
                           type_generation=args.type_gen)
            true_preferences, true_counts = data.preferences, data.counts
        else:
            raise NotImplementedError('Unknown voter source')

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
                    SN = SocialNetwork(strategy = 'dataset_and_nx_graph', possible_indecision_levels = possible_indecision_levels, \
                        graph = graph, dataset = data, print_graph = args.print_graph)

                    # and compare it under every paradigm
                    for paradigm in paradigms:

                        # for more than one experiment
                        for _ in range(args.experiments):
                            # get the preferences
                            SN_preferences, SN_counts = SN.get_preferences(paradigm,\
                                print_delegations = args.print_delegations, print_preferences = args.print_preferences)

                            # and get the winner for every rule
                            for rule in VotingRules.rules:
                                # this corresponds to random tie breaking
                                winner = VotingRules.elect(rule, SN_preferences, SN_counts, tiebreaking = lambda winners : random.choice(list(winners)))

                                regrets[graph_type][paradigm][rule].append(regret(winner, true_preferences, true_counts))
                                if args.partial_regret:
                                    partial_regrets[graph_type][paradigm][rule].append(partial_regret(winner, SN.id2voter.values()))

                                winners[graph_type][paradigm][rule][winner] += 1

                                # update the progress bar
                                pbar.update(1)

    # TODO: visualize each different graph setting differently?

    # print result
    def print_results(data, name = 'regret', print_winners = True):
        # by default, we say it is not passed
        t_tests = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : 'FAILED'))))
        for graph_type in graph_types:
            for rule in VotingRules.rules:
                for paradigm in paradigms:
                    # data
                    regs = data[graph_type][paradigm][rule]
                    print(f'avg {name} {graph_type}, {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
                    if not args.skip_print_winners and print_winners:
                        print(', '.join([f'{w} won {c} times' for w, c in sorted(dict(winners[graph_type][paradigm][rule]).items())]))
                    # t test
                    for other in paradigms:
                        if other != paradigm:
                            data1 = data[graph_type][paradigm][rule]
                            data2 = data[graph_type][other][rule]
                            stat, p = ttest_ind(data1, data2)
                            if p <= 0.05:
                                t_tests[graph_type][paradigm][other][rule] = 'PASSED'
                print("#######")

        if args.ttest:
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
    if args.partial_regret:
        print_results(partial_regrets, name = 'partial regret', print_winners = False)
