from partialorders import PartialOrder
from voter import Voter
from networks import generate_graphs
import random
from collections import Counter

import networkx as nx

class SocialNetwork:
    """Class representing the social network"""

    def __init__(self, dataset, graph = 'path', strategy = 'liquid'):
        """ Initialize the Social Network.

        Parameters:
        dataset (Dataset): contains preference information
        graph [str, dict(int, list(int))]: if str, specify a random graph generation strategy. Otherwise,
                                            specify a graph (dict) consistent with the dataset."""

        # for every preference, create COUNTS number of voters
        voter_id_count = 0
        self.id2voter = dict()
        for strict, count in zip(dataset.preferences, dataset.counts):
            for _ in range(count):
                # TODO: parametrize the indiff level
                partial = PartialOrder.generate_from_strict(strict, 1)# random.choice([0, 0.3, 1]))
                voter = Voter(partial, strict)
                self.id2voter[voter_id_count] = voter
                voter_id_count += 1

        if isinstance(graph, str):
            # generate this graph
            self.graph = list(generate_graphs(num_voters=dataset.count_voters(), num_graphs=1, gtype=graph))[0]
        elif isinstance(graph, dict):
            self.graph = nx.DiGraph(graph)
            assert len(self.graph.nodes()) == dataset.count_voters(), "The passed graph is not consistent with the dataset."
        else:
            raise NotImplementedError("Graphs can be either a string (random generation strategy) or dictionaries.")

        # data structure to memorize the delegation graph
        # will be filled in the pick_delegations func
        self.delegations = dict()
        # data structure to memorize the votes
        # will be filled in the cast_vote func
        self.votes = dict()

    def getNeighbours(self, voter_id):
        """ Returns a list of neighbours for a voter 

        Parameters:
        voter_id (int): the voter's numerical id

        Returns:
        list(int): its neighbours """

        return list(self.graph.successors(voter_id))

    def pick_delegations(self, strategy = 'liquid'):
        """ Pick the delegations for each voter. In this function, the data structure self.delegations will be filled.

        Parameters:
        strategy (str): direct voting, proxy voting or liquid democracy? """

        if strategy == 'liquid':

            # for every voter...
            for voter_id, voter in self.id2voter.items():
                # get its neighbours' ids
                neighbours_id = self.getNeighbours(voter_id)
                # and the neighbours themselves
                neighbours = [self.id2voter[neighbour_id] for neighbour_id in neighbours_id]
                # construct delegations. This will be a list.
                delegations = voter.delegate(neighbours_id, neighbours)
                # if it is empty, we do not delegate. Signal this with a None.
                if len(delegations) == 0:
                    delegations = None
                # otherwise, pick a random delegation from the list (notice that, if it is of length 1, it's simply the only element)
                else:
                    delegations = random.choice(delegations)

                self.delegations[voter_id] = delegations

        elif strategy == 'direct':
            for voter_id in self.id2voter.keys():
                self.delegations[voter_id] = None
        elif strategy == 'proxy':
            raise NotImplementedError("Proxy voting not yet available")
        else:
            raise NotImplementedError("This delegation strategy does not exist.")

    def cast_votes(self):
        """ Assign to each voter a vote. In this function, the data structure self.votes will be filled. """

        # If it was not already done, pick the delegation
        if not self.delegations:
            self.pick_delegations()

        # TODO abstain instead

        # for every voter:
        for voter_id, voter in self.id2voter.items():
            # if we don't have a vote already...
            if voter_id not in self.votes.keys():
                # if he does not delegate, then we cast a random vote.
                # Notice if that the voter is DECISIVE, this is simply equivalent
                # to getting his true order
                if self.delegations[voter_id] is None:
                    self.votes[voter_id] = voter.cast_random_vote()
                # otherwise, retrieve the vote of the person he was delegating to.
                else:
                    self.votes[voter_id] = self._retrieve_vote(self.delegations[voter_id])

    def _retrieve_vote(self, voter_id):
        """ Recursvely get the voter_id's vote from delegation graph 

        Parameters:
        voter_id (int): a voter

        Returns:
        list(int): a ballot """

        # if this person already voted, simply return the vote.
        if voter_id in self.votes.keys():
            return self.votes[voter_id]
        # otherwise...
        # if he does not delegate, 
        # save his vote and return it
        elif self.delegations[voter_id] is None:
            self.votes[voter_id] = self.id2voter[voter_id].cast_random_vote()
            return self.votes[voter_id]
        # if he does, get the vote (recursvely) of the person he delegates to
        # we save it as ours and return it
        else:
            next_vote = self._retrieve_vote(self.delegations[voter_id])
            self.votes[voter_id] = next_vote
            return next_vote

    def preference_list(self):
        """ Return the preference list of the social network. 

        Returns:
        list(int), list(int): all the ballots with their counts """

        # if it was not done already, cast the votes
        if not self.votes:
            self.cast_votes()

        # support functions because a list is not hashable
        # this enables us to use the Counter
        to_key = lambda pref: ' '.join(map(str, pref))
        to_list = lambda key: [int(val) for val in key.split()]

        # transform the votes into keys, so we can use the counter
        keys = map(to_key, self.votes.values())

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

        return preferences, counts



if __name__ == '__main__':
    # test

    from dataset import Dataset

    data = Dataset(source='random', rand_params=[4, 100])
    SN = SocialNetwork(data)
    SN.pick_delegations('direct')
    print(SN.preference_list())