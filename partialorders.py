import networkx as nx
import itertools
import random

class PartialOrder:
    """Class representing a partial order."""

    @classmethod
    def generate_from_strict(cls, strict, indecisivness):
        """ Given a strict order, generate a partial order consistent with it.

        Parameters:
        strict (list(int)): the strict order
        indecisivness (float): the degree of indecisivness the resulting partial order must have

        Returns:
        (PartialOrder): the randomly generated partial order"""


        # we begin by creating the partial order corresponding to our strict order.
        graph = dict()
        ll = list(strict)
        for a in strict:
            ll.remove(a)
            graph[a] = list(ll)
        order = PartialOrder(graph)
        
        # then, we keep removing edges untill we reach the desired indecisivness

        while True:
            # if we reached it, good, return it
            if order.compute_indecisivness() >= indecisivness:
                return order
            else:
                # pick a node with a non-empty list of edges
                head = random.choice([k for k in graph.keys() if graph[k]])
                # random node connected to it
                tail = random.choice(graph[head])
                # remove it
                graph[head].remove(tail)
                order = PartialOrder(graph)


    def __init__(self, partial):
        """Initialize the object with a partial.

        Parameters:
        partial (dict(int, list(int))): a partial order, represented as an adjacency list
        """
        self.partial = partial
        # will be populated at the first call of get_strict_orders
        self._strict_orders = None

        # max number of strict orders with this alternatives: will be used in a function
        factorial = lambda n : 1 if n <= 1 else n * factorial(n-1)
        self.MAX_STRICT_ORDERS = factorial(len(partial))

    def get_strict_orders(self):
        """given a partial order, return all the strict orders consistent with it

        Returns:
        list(list(int)): strict orders"""

        # General idea: topological orders

        # we save it in _strict_orders to avoid recomputing it

        if self._strict_orders is None:
            G = nx.DiGraph(self.partial)
            self._strict_orders = list(nx.algorithms.dag.all_topological_sorts(G))

        return self._strict_orders

    def check_consistency(self, other):
        """ Check whether this partial order is consistent with another (i.e. they share a strict order).

        Parameters:
        other ([PartialOrder, list(int)]): another order. Can be either a partial orther or a strict order

        Returns:
        (bool): the verdict"""

        my_strict_orders = self.get_strict_orders()

        if isinstance(other, PartialOrder):
            for strict_order in other.get_strict_orders():
                if strict_order in my_strict_orders:
                    return True

            return False
        # it is a strict order
        else:
            return other in my_strict_orders

    # this might not be a good score
    def compute_indecisivness(self):
        """ Give "indecisivness" score (i.e., number of consistent strict orders) to self (normalized)

        Returns:
        (float): the score"""

        return (len(self.get_strict_orders()) - 1) / (self.MAX_STRICT_ORDERS - 1)

    def random_strict_order(self):
        """ Return a random strict order consistent with the partial order represented by self

        Returns:
        (list(int)): a strict order"""

        return random.choice(self.get_strict_orders())

    def pick_delegation(self, orders, criteria = 'min_indecision'):
        """ Choose whom to delegate to. Criteria: among those who are consistent, pick 
        the less indecisive. If none is consistent, return none."

        Parameters:
        orders (dict(t, PartialOrder)): pool of partial orders to choose from. "t" indicates a generic type (will probably be int)
        criteria (str): specify which criteria to use.

        Returns:
        ([list(t), None]): indexes of the choosen partial orders OR None if none was available!"""


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

        elif criteria == 'random': # randomly pick a consistent parital order
            consistent_preorders = [i for i,p in preorders.items() if self.check_consistency(p)]
            candidadate_list = [random.choice(consistent_preorders)] if consistent_preorders else None
            
        else:
            raise NotImplementedError('This delegation strategy has not been implemented.')

        # three cases: none, one or more than one
        return candidadate_list