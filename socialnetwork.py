from partialorders import PartialOrder
from voter import Voter
from networks import generate_graphs
import random
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt

class SocialNetwork:
    """Class representing the social network"""

    def __init__(self, strategy = '', print_graph = False, id2voter = None, graph = None, dataset = None, graph_generation = None, graph_seed = None):
        """ Initialize the Social Network.

        Parameters:
        strategy (str): generation strategy of the graph
        print_graph (bool): whether to print the graph just created """

        if strategy == 'from_voter_graph':
            assert isinstance(id2voter, dict) and isinstance(graph, dict)
            assert id2voter.keys() == graph.keys()
            self.id2voter = id2voter
            self.graph = nx.DiGraph(graph)
        elif strategy == 'dataset_and_random_edges':
            # for every preference, create COUNTS number of voters
            voter_id_count = 0
            self.id2voter = dict()
            for strict, count in zip(dataset.preferences, dataset.counts):
                for _ in range(count):
                    # TODO: parametrize the indiff level!!
                    partial = PartialOrder.generate_from_strict(strict, random.choice([0, 0.2, 1]))
                    voter = Voter(partial, strict)
                    self.id2voter[voter_id_count] = voter
                    voter_id_count += 1
            self.graph = list(generate_graphs(num_voters=dataset.count_voters(), num_graphs=1, gtype=graph_generation, seed = graph_seed))[0]
        else:
            raise NotImplementedError("This graph-creation strategy does not exist.")

        if print_graph:
            nx.draw(self.graph, with_labels=True, font_weight='bold')
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
            # first round: pick decisive voters
            for voter_id, voter in self.id2voter.items():
                if len(voter.partial.get_strict_orders()) == 1:
                    delegations[voter_id] = None

            # second round: indecisive voters find guru to delegate, or vote randomly
            for voter_id, voter in self.id2voter.items():
                assert voter_id >= 0, 'voter id must be positive'
                try:
                    # skip decisive voters that vote already
                    if delegations[voter_id] == None:
                        continue
                except KeyError:
                    # get its neighbours' ids
                    neighbours_id = self.getNeighbours(voter_id)
                    # and the neighbours themselves
                    neighbours = [self.id2voter[neighbour_id] for neighbour_id in neighbours_id]
                    # get viable delegations
                    delegation = voter.delegate(neighbours_id, neighbours)
                    # if no delegation is available we do not delegate
                    if len(delegation) == 0:
                        # use a '-1' placeholder; switch for None afterwards
                        delegation = -1
                    else:
                        delegation = self._filter_delegations(delegation, delegations)
                        delegation = random.choice(delegation)
                    delegations[voter_id] = delegation

            delegations = {i: None if j == -1 else j for i, j in delegations.items()}

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

    def _filter_delegations(self, d, delegations):
        """ Take a list of possible delegations and filter out voters that
        do not vote themselves (for proxy voting)

        Parameters:
        d list(int): list of possible delegations for particular voter
        delegations dict(int, [int, NoneType]): delegation mapping

        Returns:
        list(int)"""

        filt_d = []
        for voter in d:
            try:
                # add a voter id iff the voter declared to vote in 1st round
                if delegations[voter] == None:
                    filt_d.append(voter)
            except:
                # voter has no declared delegation decision=> he did not choose to vote in 1st round
                pass
        # iff there is nobody to delegate to, use the proxy-voting placeholder
        if len(filt_d) == 0:
            filt_d.append(-1)

        return filt_d

    def get_preferences(self, paradigm = 'liquid', print_delegations = False, print_preferences = False):
        """ Return the preference list of the social network. This function 
        creates the delegations, casts the votes and returns the preference lists.

        Parameters:
        paradigm (str): which paradigm? (liquid, direct, proxy...)
        print_delegations (bool): whether to print the selected delegations
        print_preferences (bool): print the preferences nicely

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

        if print_preferences:
            self.pretty_print_pref(preferences, counts)

        return preferences, counts

    def pretty_print_pref(self, preferences, counts):
        """ Print cutely the preferences of the electorate
        
        Parameters:
        preferences (list(list(int))): ballots
        counts (list(int)): one per each ballot; number of people who submitted that ballot """

        for pref, count in sorted(zip(preferences, counts), key = lambda x: -x[1]):
            print(f"{count} voters think that {pref}")