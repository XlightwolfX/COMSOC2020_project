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
        order = PartialOrder(strict)
        graph = dict(order.partial)
        
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


    def __init__(self, inpt):
        """Initialize the object with a partial.

        Parameters:
        inpt ([dict(int, list(int)), list(int)]): either a partial order, represented as an adjacency list, or a strict order.
        """
        if isinstance(inpt, dict):
            partial = inpt
        else:
            # it is a strict order / list. Generate it from here.
            partial = dict()
            ll = list(inpt)
            for a in inpt:
                ll.remove(a)
                partial[a] = list(ll)

        self.partial = partial
        # will be populated at the first call of get_strict_orders
        self._strict_orders = None

        # max number of strict orders with this alternatives: will be used in a function
        factorial = lambda n : 1 if n <= 1 else n * factorial(n-1)
        self.MAX_STRICT_ORDERS = factorial(len(partial))

    def __repr__(self):
        """`to string` method"""
        return str(self.partial)

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
            for mine, other in zip(my_strict_orders, other.get_strict_orders()):
                if mine == other:
                    return True
            return False

        # it is a strict order
        elif isinstance(other, list):
            return other in my_strict_orders
        else:
            raise NotImplementedError

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