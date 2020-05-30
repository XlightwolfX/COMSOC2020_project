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

import multiprocessing


def worker(procnum, return_dict, args, possible_indecision_levels, paradigms, graph_type, graphs):
    winners = dict()
    regrets = dict()
    partial_regrets = dict()

    for paradigm in paradigms:
        winners[paradigm] = dict()
        regrets[paradigm] = dict()
        partial_regrets[paradigm] = dict()
        for rule in VotingRules.rules:
            winners[paradigm][rule] = dict()
            regrets[paradigm][rule] = []
            partial_regrets[paradigm][rule] = []

    for graph in graphs:
        for _ in range(args.experiments):
            data = Dataset(source='type_random', rand_params=[args.alternatives, args.voters, args.voter_types],
                           type_generation=args.type_gen)
            true_preferences, true_counts = data.preferences, data.counts
            SN = SocialNetwork(strategy = 'dataset_and_nx_graph', possible_indecision_levels = possible_indecision_levels, \
                               graph = graph, dataset = data, print_graph = args.print_graph)
            for paradigm in paradigms:

                # for more than one experiment
                # get the preferences
                SN_preferences, SN_counts = SN.get_preferences(paradigm,\
                    print_delegations = args.print_delegations, print_preferences = args.print_preferences)

                # and get the winner for every rule
                for rule in VotingRules.rules:
                    # this corresponds to random tie breaking
                    winner = VotingRules.elect(rule, SN_preferences, SN_counts, tiebreaking = lambda wins : random.choice(list(wins)))

                    regrets[paradigm][rule].append(regret(winner, true_preferences, true_counts))
                    if args.partial_regret:
                        partial_regrets[paradigm][rule].append(partial_regret(winner, SN.id2voter.values()))
                    if winner not in winners[paradigm][rule]:
                        winners[paradigm][rule][winner] = 0
                    winners[paradigm][rule][winner] += 1
    return_dict['winners' + str(procnum)] = winners
    return_dict['regrets' + str(procnum)] = regrets
    return_dict['partial_regrets' + str(procnum)] = partial_regrets
    return

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
    # parser.add_argument('--indecisiveness', type=float, nargs='+', default=[0.0, 0.043478260869565216, 0.08695652173913043, 0.13043478260869565, 0.17391304347826086, 0.21739130434782608, 0.30434782608695654, 0.4782608695652174, 1.0],
    #                     help="indecisiveness distribution")
    parser.add_argument('--indecisiveness', type=float, nargs='+', default=[0, 0.3, 0.3, 0.3, 0.47, 0.47, 0.47, 1, 1, 1],
                        help="indecisiveness distribution")

    args = parser.parse_args()

    random.seed(args.seed)

    graph_types = ['regular']
    paradigms = ['direct', 'proxy', 'liquid']

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

    # possible_indecision_levels = ind_levels(args.alternatives)
    possible_indecision_levels = args.indecisiveness
    pr = reversed([0.18701423, 0.18126041, 0.16503948, 0.14116575, 0.11342986, 0.08562135, 0.06071463, 0.04044466, 0.02530962])

    # progress bar
    with tqdm(total=TOT_EXPERIMENTS, leave = False) as pbar:
        # for all types of graphs
        for graph_type in graph_types:

            # for all parameters settings of this graph
            for params in param_generator(graph_type):

                # generate some graphs with this parameters
                graph_generator = generate_graphs(num_voters=args.voters, \
                    num_graphs=args.graphs_per_setting, gtype=graph_type, seed = args.seed, params = params)

                # for every graph
                    # get the corresponding SN

                    # and compare it under every paradigms
                w = 0
                manager = multiprocessing.Manager()
                return_dict = manager.dict()
                jobs = []
                graphs = []

                for i, graph in enumerate(graph_generator):
                    graphs.append(graph)

                    if len(graphs) == 5:
                        p = multiprocessing.Process(target=worker, args=(w, return_dict, args, possible_indecision_levels, paradigms, graph_type, graphs))
                        jobs.append(p)
                        p.start()
                        w += 1
                        graphs = []
                for proc in jobs:
                    proc.join()
                    pbar.update(args.experiments * 5 * 3)

                for ii in range(w):
                    for paradigm in paradigms:
                        for rule in VotingRules.rules:
                            regrets[graph_type][paradigm][rule] += return_dict['regrets' + str(ii)][paradigm][rule]
                            # partial_regrets[graph_type][paradigm][rule] += return_dict['partial_regrets'][paradigm][rule]
                            for winner in [1, 2, 3, 4]:
                                winners[graph_type][paradigm][rule][winner] += return_dict['winners' + str(ii)][paradigm][rule].get(winner, 0)


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
                    with open('results/{}_{}_{}_types.txt'.format(graph_type, paradigm, rule), 'a+') as f:
                        f.write('{:.4f},{:.4f}\n'.format(np.mean(regs), np.std(regs)))
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
