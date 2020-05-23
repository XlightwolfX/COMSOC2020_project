from socialnetwork import SocialNetwork
import argparse
import numpy as np
from tqdm import tqdm
from utils import regret, partial_regret
from collections import defaultdict
from votingrules import VotingRules

seed = 42
def random_graph(args):
    global seed

    from dataset import Dataset

    data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
    true_preferences, true_counts = data.preferences, data.counts
    SN = SocialNetwork(strategy = 'dataset_and_random_edges', dataset = data, graph_generation = args.graph_type, graph_seed = seed, print_graph = args.print_graph)

    seed += 1

    return SN, true_preferences, true_counts

def case_study_star(args):
    from voter import Voter
    from partialorder import PartialOrder
    import itertools
    # this is a simple case study where everyone is connected to a center
    # everybody has a true strict order 1,2,3,4
    # only the center knows it
    center_voter = Voter(PartialOrder({1:[2,3,4], 2:[3,4], 3:[4], 4:[]}), [1,2,3,4])
    id2voter = {0: center_voter}
    graph = {0: []}
    for i, ll in enumerate(list(itertools.permutations([1, 2, 3, 4]))):
        ll = list(ll)
        if ll != [1,2,3,4]:
            id2voter[i] = Voter(PartialOrder({1:[], 2:[], 3:[], 4:[]}), [1,2,3,4])
            graph[i] = [0]

    true_preferences = [voter.strict for voter in id2voter.values()]
    true_counts = [1] * len(true_preferences)
    SN = SocialNetwork(strategy = 'from_voter_graph', id2voter = id2voter, graph = graph, print_graph = args.print_graph)

    return SN, true_preferences, true_counts


def typed_graph(args):
    import random
    from voter import Voter
    from partialorders import PartialOrder
    from voter_type import VoterTypes

    def voter_type(i):
        return [1,2,3,4] if i % 2 == 0 else ([2,1,3,4] if i % 3 == 0 else [3,1,2,4])

    def cotyped(i, j):
        return voter_type(i) == voter_type(j)

    N = args.voters

    gen_normal = VoterTypes(2)
    # generate a graph where the voters have two types
    id2voter = dict()
    for i in range(N):
        # strict = voter_type(i)
        strict = gen_normal.generate()
        # second parameter is indecisivness, i put these arbitrary probabilities
        partial = PartialOrder.generate_from_strict(strict, random.choice([0] + [0.2] * 2 + [1] * 7))
        # partial = PartialOrder.generate_from_strict(strict, np.random.choice(indecisivness, p=ps))
        voter = Voter(partial, strict)
        id2voter[i] = voter

    # random graph
    graph = dict()
    for i in range(N):
        graph[i] = []
        for j in range(N):
            if i != j:
                thresh = 0.5 # 0.7 if cotyped(i, j) else 0.3
                if random.random() <= thresh:
                    graph[i].append(j)

    true_preferences = [voter.strict for voter in id2voter.values()]
    true_counts = [1] * len(true_preferences)
    SN = SocialNetwork(strategy = 'from_voter_graph', id2voter = id2voter, graph = graph, print_graph = args.print_graph)

    return SN, true_preferences, true_counts

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--alternatives', type=int, default=4, help='Number of alternatives.')
    parser.add_argument('--voters', type=int, default=1000, help='Number of voters.')
    parser.add_argument('--experiments', type=int, default=500, help='Number of experiments.')
    parser.add_argument('--experiment_type', type=str, default='random_graph', help='Which experiments?')
    parser.add_argument('--graph_type', type=str, default='path', help='Type of graph to be generated')
    parser.add_argument('--print_graph', action='store_true', help='Print the generated graph')
    parser.add_argument('--print_delegations', action='store_true', help='Print the delegation chains')
    parser.add_argument('--print_preferences', action='store_true', help='Print the preference counts')
    parser.add_argument('--use_partial_regret', action='store_true', help='Use the alternative metric of partial regret instead.')

    args = parser.parse_args()

    experiments = {'random_graph': random_graph, 'typed_graph': typed_graph, 'case_study_star': case_study_star}

    try :
        experiment = experiments[args.experiment_type]
    except KeyError:
        raise Exception(f"Experiment {args.experiment_type} does not exist. Possible experiments: {list(experiments.keys())}")

    # comparing direct and liquid
    for paradigm in ['direct', 'proxy', 'liquid']:
        # datastructure used to compute avg regret and distribution of winners
        regrets = defaultdict(lambda : [])
        winners = defaultdict(lambda : 0)
        # repeat the experiment N times
        for _ in tqdm(range(args.experiments)):
            # get SN and preferences
            SN, true_preferences, true_counts = experiment(args)

            # run the delegation mechanism, assign a preference to everybody a count the ballots
            SN_preferences, SN_counts = SN.get_preferences(paradigm,
                print_delegations = args.print_delegations, print_preferences = args.print_preferences)

            # per every rule...
            for rule in VotingRules.rules:
                # min == lexicographic rule
                winner = VotingRules.elect(rule, SN_preferences, SN_counts, tiebreaking = min)
                winners[winner] += 1
                # note: if here we use SN_preferences, SN_counts we compute the regret
                # on the "reported" ballots not the TRUE preferences.
                # Interestingly, if here we use SN_preferences, SN_counts, liquid democracy
                # vastly outperform direct...
                # TODO: investigate this!

                if args.use_partial_regret:
                    regrets[rule].append(partial_regret(winner, SN.id2voter.values()))
                else:
                    regrets[rule].append(regret(winner, true_preferences, true_counts))

        print(f"## average {'partial ' if args.use_partial_regret else ''}regret of `{paradigm}` paradigm ##")
        for rule, val in regrets.items():
            val = np.array(val)
            print(f'{rule}: {val.mean():.4f} (+-{val.std():.4f})')
        # TODO main issue: it seems like using either mechanism does not make any difference in result.
        print(f'\ncounts of winners: {[(wnnr, cnt) for wnnr, cnt in winners.items()]}')
        print(f'#####')
