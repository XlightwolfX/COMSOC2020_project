import networkx as nx
import itertools
import random

class Preorder:
    """Class representing a preorder. Note: a->b means that "a is at least as good as b", hence the cycles. """

    def __init__(self, preorder):
        """Initialize the object with a preorder.

        Parameters:
        preorder (dict(int, list(int))): a preorder, represented as an adjacency list
        """
        self.preorder = preorder
        # will be populated at the first call of get_strict_orders
        self._strict_orders = None

        # max number of strict orders with this alternatives: will be used in a function
        factorial = lambda n : 1 if n <= 1 else n * factorial(n-1)
        self.MAX_STRICT_ORDERS = factorial(len(preorder))

    def _get_all_partial_orders(self):
        """given a preorder, return all the partial orders consistent with it

        Returns:
        list(list(set(int))): all partial orders"""

        # General idea:
        # first, we construct the supergraph composed of condensated strongly connected components
        # then, we get all the topological sorts of it
        # the results is simply that. We only substitute the supernodes with the original set of nodes they represent!

        G = nx.DiGraph(self.preorder)

        scc = nx.algorithms.components.strongly_connected_components(G)
        super_G = nx.algorithms.components.condensation(G, scc)
        
        top_sorts = nx.algorithms.dag.all_topological_sorts(super_G)
        return [[super_G.nodes[node]['members'] for node in sort] for sort in top_sorts]

    def _partial2strict(self, partial_order):
        """given a partial order, return all the strict orders consistent with it

        Parameters:
        partial_order list(set(int)): partial order (a list of sets, and being in the same set = being equivalent)

        Returns:
        list(list(int)): strict orders"""

        # orders "derived" from this order
        strict_orders = []

        # each element is a set of "equivalent" elements 
        for element in partial_order:
            # if a = b, then we can get a > b or b > a (i.e., permutations)
            all_perms = list(itertools.permutations(list(element)))

            # add all the possible permutations to all the orders we have derived up to this point
            if strict_orders:
                strict_orders = [o+p for o in strict_orders for p in all_perms]
            # base case if no order yet
            else:
                strict_orders = all_perms

        return strict_orders

    def get_strict_orders(self):
        """given a preorder, return all the strict orders consistent with it

        Returns:
        list(list(int)): strict orders"""

        if self._strict_orders is None:
            partial_orders = self._get_all_partial_orders()
            self._strict_orders = []
            # for each partial order, get the consistent orders
            for partial_order in partial_orders:
                self._strict_orders += self._partial2strict(partial_order)

        return self._strict_orders

    def check_consistency(self, other_preorder):
        """ Check whether this preorder is consistent with another (i.e. they share a strict order).

        Parameters:
        other_preorder (Preorder): another preorder

        Returns:
        (bool): the verdict"""
        my_strict_orders = self.get_strict_orders()

        for strict_order in other_preorder.get_strict_orders():
            if strict_order in my_strict_orders:
                return True

        return False

    def compute_indecisivness(self):
        """ Give "indecisivness" score (i.e., number of consistent strict orders) to self (normalized)

        Returns:
        (float): the score"""

        return (len(self.get_strict_orders()) - 1) / (self.MAX_STRICT_ORDERS - 1)

    def random_strict_order(self):
        """ Return a random strict order consistent with the preorder

        Returns:
        (list(int)): a strict order"""
        return random.choice(self.get_strict_orders())

    def pick_delegation(self, preorders, criteria = 'min_indecision'):
        """ Choose whom to delegate to. Criteria: among those who are consistent, pick 
        the less indecisive. If none is consistent, return none."

        Parameters:
        preorders (dict(t, Preorder)): pool of preorders to choose from. "t" indicates a generic type (will probably be int)
        criteria (str): specify which criteria to use.

        Returns:
        ([list(t), None]): indexes of the choosen preorders OR None if none was available!"""


        if criteria == 'min_indecision': # pick alternative that minimizes indecision
            min_score = float('inf')
            candidadate_list = None

            for i, p in preorders.items():
                if self.check_consistency(p):
                    score = p.compute_indecisivness()
                    if score < min_score:
                        min_score = score
                        candidadate_list = [i]
                    elif score == min_score:
                        candidadate_list.append(i)
        elif criteria == 'random': # randomly pick a consistent preorder
            consistent_preorders = [i for i,p in preorders.items() if self.check_consistency(p)]
            candidadate_list = [random.choice(consistent_preorders)] if consistent_preorders else None
        else:
            raise NotImplementedError('This delegation strategy has not been implemented.')

        # three cases: none, one or more than one
        return candidadate_list