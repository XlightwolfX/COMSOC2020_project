from partialorders import PartialOrder
from voter import Voter
from networks import generate_graphs
import random
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt

class SocialNetwork:
    """Class representing the social network"""

    def __init__(self, dataset, graph = 'scale-free', print_graph = False):
        """ Initialize the Social Network.

        Parameters:
        dataset (Dataset): contains preference information
        graph [str, dict(int, list(int))]: if str, specify a random graph generation strategy. Otherwise,
                                            specify a graph (dict) consistent with the dataset.
        print_graph (bool): whether to print the graph just created """

        # for every preference, create COUNTS number of voters
        voter_id_count = 0
        self.id2voter = dict()
        for strict, count in zip(dataset.preferences, dataset.counts):
            for _ in range(count):
                # TODO: parametrize the indiff level
                partial = PartialOrder.generate_from_strict(strict, random.choice([0, 0.2, 1]))
                voter = Voter(partial, strict)
                self.id2voter[voter_id_count] = voter
                voter_id_count += 1

        if isinstance(graph, str):
            # generate this type of graph
            self.graph = list(generate_graphs(num_voters=dataset.count_voters(), num_graphs=1, gtype=graph))[0]
        elif isinstance(graph, dict):
            self.graph = nx.DiGraph(graph)
            assert len(self.graph.nodes()) == dataset.count_voters(), "The passed graph is not consistent with the dataset."
        else:
            raise NotImplementedError("Graphs can be either a string (random generation strategy) or dictionaries.")

        if print_graph:
            nx.draw(self.graph)
            plt.show()

    def getNeighbours(self, voter_id):
        """ Returns a list of neighbours for a voter 

        Parameters:
        voter_id (int): the voter's numerical id

        Returns:
        list(int): its neighbours """

        return list(self.graph.successors(voter_id))

    def _pick_delegations(self, paradigm = 'liquid', print_delegations = False):
        """ Pick the delegations for each voter. 

        Parameters:
        paradigm (str): direct voting, proxy voting or liquid democracy? 
        print_delegations (bool): whether to print the selected delegations

        Returns:
        dict(int, [int, NoneType]): a mapping from a voter id to another """

        delegations = dict()

        if paradigm == 'liquid':

            # for every voter...
            for voter_id, voter in self.id2voter.items():
                # get its neighbours' ids
                neighbours_id = self.getNeighbours(voter_id)
                # and the neighbours themselves
                neighbours = [self.id2voter[neighbour_id] for neighbour_id in neighbours_id]
                # construct delegations. This will be a list.
                delegation = voter.delegate(neighbours_id, neighbours)
                # if it is empty, we do not delegate. Signal this with a None.
                if len(delegation) == 0:
                    delegation = None
                # otherwise, pick a random delegation from the list (notice that, if it is of length 1, it's simply the only element)
                else:
                    delegation = random.choice(delegation)

                delegations[voter_id] = delegation

        elif paradigm == 'direct':
            for voter_id in self.id2voter.keys():
                delegations[voter_id] = None
        elif paradigm == 'proxy':
            raise NotImplementedError("Proxy voting not yet available")
        else:
            raise NotImplementedError("This delegation strategy does not exist.")

        if print_delegations:
            for i, j in delegations.items():
                if j is not None:
                    print(f"{i} -> {j}")

        return delegations

    def _cast_votes(self, paradigm = 'liquid', print_delegations = False):
        """ Assign to each voter a vote. 

        Parameters:
        paradigm (str): which paradigm? (liquid, direct, proxy...) 
        print_delegations (bool): whether to print the selected delegations

        Returns:
        dict(int, list(int)): a mapping from a voter id to a preference """

        # pick the delegation
        delegations = self._pick_delegations(paradigm, print_delegations)

        votes = dict()

        # for every voter:
        for voter_id in self.id2voter.keys():
            votes[voter_id] = self._retrieve_vote(voter_id, votes, delegations)

        return votes

    def _retrieve_vote(self, voter_id, votes, delegations):
        """ Recursvely get the voter_id's vote from delegation graph 

        Parameters:
        voter_id (int): a voter
        votes dict(int, list(int)): a mapping from a voter id to a preference 
        delegations (dict(int, [int, NoneType]): delegations from voter id to another

        Returns:
        list(int): a ballot """

        # if this person already voted, simply return the vote.
        if voter_id in votes.keys():
            return votes[voter_id]
        # otherwise...
        # if he does not delegate, 
        # save his vote and return it
        elif delegations[voter_id] is None:
            votes[voter_id] = self.id2voter[voter_id].cast_random_vote()
            return votes[voter_id]
        # if he does, get the vote (recursvely) of the person he delegates to
        # we save it as ours and return it
        else:
            next_vote = self._retrieve_vote(delegations[voter_id], votes, delegations)
            votes[voter_id] = next_vote
            return next_vote

    def get_preferences(self, paradigm = 'liquid', print_delegations = False, pretty_print = False):
        """ Return the preference list of the social network. This function 
        creates the delegations, casts the votes and returns the preference lists.

        Parameters:
        paradigm (str): which paradigm? (liquid, direct, proxy...)
        print_delegations (bool): whether to print the selected delegations
        pretty_print (bool): print the preferences nicely

        Returns:
        list(int), list(int): all the ballots with their counts """

        # cast the votes
        votes = self._cast_votes(paradigm, print_delegations)

        # support functions because a list is not hashable
        # this enables us to use the Counter
        to_key = lambda pref: ' '.join(map(str, pref))
        to_list = lambda key: [int(val) for val in key.split()]

        # transform the votes into keys, so we can use the counter
        keys = map(to_key, votes.values())

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

        assert (sum(counts) == len(self.id2voter.keys()))

        if pretty_print:
            self.pretty_print_pref(preferences, counts)

        return preferences, counts

    def pretty_print_pref(self, preferences, counts):
        """ Print cutely the preferences of the electorate
        
        Parameters:
        preferences (list(list(int))): ballots
        counts (list(int)): one per each ballot; number of people who submitted that ballot """

        for pref, count in sorted(zip(preferences, counts), key = lambda x: -x[1]):
            print(f"{count} voters think that {pref}")


if __name__ == '__main__':
    # test

    # test-specific imports
    import argparse
    from dataset import Dataset
    import numpy as np
    from tqdm import tqdm
    from utils import regret, partial_regret
    from votingrules import VotingRules
    from collections import defaultdict

    parser = argparse.ArgumentParser()
    parser.add_argument('--alternatives', type=int, default=4, help='Number of alternatives.')
    parser.add_argument('--voters', type=int, default=3000, help='Number of voters.')
    parser.add_argument('--experiments', type=int, default=500, help='Number of experiments.')

    args = parser.parse_args()

    # create the SN
    data = Dataset(source='random', rand_params=[args.alternatives, args.voters])
    true_preferences, true_counts = data.preferences, data.counts
    SN = SocialNetwork(data, graph = 'random', print_graph = True)
    
    # comparing direct and liquid
    for paradigm in ['direct', 'liquid']:
        # datastructure used to compute avg regret and distribution of winners
        regrets = defaultdict(lambda : [])
        winners = defaultdict(lambda : 0)
        # repeat the experiment N times
        for _ in tqdm(range(args.experiments)):
            # run the delegation mechanism, assign a preference to everybody a count the ballots
            SN_preferences, SN_counts = SN.get_preferences(paradigm)

            # per every rule...
            for rule in VotingRules.rules:
                # min == lexicographic rule
                winner = VotingRules.elect(rule, true_preferences, true_counts, tiebreaking = min)
                winners[winner] += 1
                # note: if here we use SN_preferences, SN_counts we compute the regret
                # on the "reported" ballots not the TRUE preferences.
                # Interestingly, if here we use SN_preferences, SN_counts, liquid democracy
                # vastly outperform direct...
                # TODO: investigate this!

                # regular regret
                regrets[rule].append(regret(winner, data.preferences, data.counts))

                # partial regret
                # regrets[rule].append(partial_regret(winner, SN.id2voter.values()))

        print(f'## average regret of `{paradigm}` paradigm ##')
        for rule, val in regrets.items():
            val = np.array(val)
            print(f'{rule}: {val.mean():.4f} (+-{val.std():.4f})')
        # TODO main issue: it seems like using either mechanism does not make any difference in result.
        print(f'\ncounts of winners: {[(wnnr, cnt) for wnnr, cnt in winners.items()]}')
        print(f'#####')