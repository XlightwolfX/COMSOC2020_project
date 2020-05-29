import argparse
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
from networks import generate_graphs
from itertools import permutations
from collections import Counter, defaultdict
from voter_type import VoterTypes
from socialnetwork import SocialNetwork
from partialorders import PartialOrder
from utils import ind_levels, regret
from voter import Voter
from votingrules import VotingRules
from tqdm import tqdm

# given a dictionary of voters,
# return two lists:
# one is a list of lists of integers (the preferences)
# one is a list of integers (how many people have that preference)
def get_counts(id2voter):
    # this enables us to use the Counter
    to_key = lambda pref: ' '.join(map(str, pref))
    to_list = lambda key: [int(val) for val in key.split()]

    # transform the votes into keys, so we can use the counter
    all_preferences = [voter.strict for voter in id2voter.values()]
    keys = map(to_key, all_preferences)

    # count the preferences
    counter = Counter(keys)
    # prepare results

    preferences, counts = [], []
    # for every possible preference (now expressed as a string) and its count
    for key_pref, count in counter.items():
        # regenerate the preference list from the string and add it to the result...
        preferences.append(to_list(key_pref))
        # ...along with its count
        counts.append(count)

    assert (sum(counts) == len(id2voter.keys()))

    return preferences, counts



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_cliques', type=int, default=6, help='Number of cliques.')
    parser.add_argument('--clique_size', type=int, default=30, help='clique size')
    parser.add_argument('--seed', type=int, default=42, help='rand seed')
    parser.add_argument('--experiments', type=int, default=100, help='rand seed')
    parser.add_argument('--indecisiveness', type=float, nargs='+', default=[0 0 0 0.3 0.3 1],
        help="indecisiveness distribution")
    args = parser.parse_args()

    random.seed(args.seed)
    paradigms = ['direct', 'proxy', 'liquid']
    type_num = args.num_cliques

    all_types = list(permutations([1,2,3,4]))

    regrets = defaultdict(lambda : defaultdict(lambda : []))
    winners = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : 0)))

    # generate one graph
    graph = list(generate_graphs(args.num_cliques * args.clique_size, 1, 'caveman', args.seed, {'clique_size': args.clique_size}))[0]

    # voter-type sampler
    generator = VoterTypes(type_num, 'half_normal')
    possible_indecision_levels = args.indecisiveness

    # progress bar
    with tqdm(total=args.experiments**2, leave=False) as pbar:

        for _ in range(args.experiments):
            id2voter = {}

            random.shuffle(all_types)
            type_list = all_types[:type_num]
            
            for i in range(type_num):
                t = type_list[i]
                for j in range(i * args.clique_size,(i + 1) *  args.clique_size):
                    strict = generator.generate(list(t))
                    # strict = list(t)
                    partial = PartialOrder.generate_from_strict(strict, random.choice(possible_indecision_levels))
                    voter = Voter(partial, strict)
                    id2voter[j] = voter

            SN = SocialNetwork(strategy='from_voter_graph', id2voter=id2voter, graph=graph)

            true_preferences, true_counts = get_counts(id2voter)

            for _ in range(args.experiments):
                for paradigm in paradigms:


                    # get the preferences
                    SN_preferences, SN_counts = SN.get_preferences(paradigm)

                    # and get the winner for every rule
                    for rule in VotingRules.rules:
                        # this corresponds to random tie breaking
                        winner = VotingRules.elect(rule, SN_preferences, SN_counts,
                                                   tiebreaking=lambda winners: random.choice(list(winners)))

                        regrets[paradigm][rule].append(regret(winner, true_preferences, true_counts))

                        winners[paradigm][rule][winner] += 1

                pbar.update(1)

    for rule in VotingRules.rules:
        for paradigm in paradigms:
            # data
            regs = regrets[paradigm][rule]
            print(f'avg regret {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
            print(', '.join([f'{w} won {c} times' for w, c in sorted(dict(winners[paradigm][rule]).items())]))
        print('---------')
