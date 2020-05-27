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
    parser.add_argument('--voters', type=int, default=100, help='Number of voters.')
    parser.add_argument('--clique', type=int, default=25, help='clique size')
    parser.add_argument('--seed', type=int, default=42, help='rand seed')
    parser.add_argument('--experiments', type=int, default=100, help='rand seed')
    args = parser.parse_args()

    random.seed(args.seed)
    paradigms = ['direct', 'proxy', 'liquid']
    type_num = args.voters // args.clique
    type_list = permutations([1,2,3,4])

    # type_list = [
    #     [1,2,3,4], [1,3,2,4], [2,1,3,4], [2,3,1,4]
    # ]

    regrets = defaultdict(lambda : defaultdict(lambda : []))
    winners = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : 0)))

    graph = list(generate_graphs(args.voters, 1, 'caveman', args.seed, {'clique_size': args.clique}))[0]

    # nx.draw(graph, with_labels=True, font_weight='bold')
    # plt.show()

    generator = VoterTypes(type_num, 'half_normal')
    pil = ind_levels(4)
    # possible_indecision_levels = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # possible_indecision_levels = [0, 1, 0.2]
    possible_indecision_levels = [0, 0.2, 0.2, 0.2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    print(pil)
    exit()
    for _ in tqdm(range(args.experiments), leave=False):
        id2voter = {}

        for i in range(type_num):
            t = type_list[i]
            for j in range(i * args.clique,(i + 1) *  args.clique):
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

    for rule in VotingRules.rules:
        for paradigm in paradigms:
            # data
            regs = regrets[paradigm][rule]
            print(f'avg regret {rule}, {paradigm}: {np.mean(regs):.4f} (+- {np.std(regs):.4f})')
            print(', '.join([f'{w} won {c} times' for w, c in sorted(dict(winners[paradigm][rule]).items())]))
        print('---------')
