import networkx as nx
import itertools

def get_all_partial_orders(alternatives, preorder):
    """given a preorder, return all the partial orders consistent with it

    Parameters:
    alternatives (set(int)): all the possible alternatives
    preorder (set((int,int))): a preorder, represented as a set of edges between alternatives

    Returns:
    list(list(set(int))): all partial orders"""

    # General idea:
    # first, we construct the supergraph composed of condensated strongly connected components
    # then, we get all the topological sorts of it
    # the results is simply that. We only substitute the supernodes with the original set of nodes they represent!

    G = nx.DiGraph()
    for a in alternatives:
        G.add_node(a)
    for source, sink in preorder:
        G.add_edge(source, sink)

    scc = nx.algorithms.components.strongly_connected_components(G)
    super_G = nx.algorithms.components.condensation(G, scc)
    
    top_sorts = nx.algorithms.dag.all_topological_sorts(super_G)
    return [[super_G.nodes[node]['members'] for node in sort] for sort in top_sorts]

def partial2strict(partial_orders):
    """given a list of partial orders, return all the strict orders consistent with them

    Parameters:
    partial_orders list(list(set(int))): list partial orders (each is a list of sets)

    Returns:
    list(list(int)): strict orders"""

    strict_orders = []
    for partial in partial_orders:
        # orders "derived" from this order
        iter_order = []

        # each element is a set of "equivalent" elements 
        for element in partial:

            # if a = b, then we can get a > b or b > a (i.e., permutations)
            all_perms = list(itertools.permutations(list(element)))

            # add all the possible permutations to all the orders we have derived up to this point
            if iter_order:
                iter_order = [o+p for o in iter_order for p in all_perms]
            # base case if no order yet
            else:
                iter_order = all_perms
        strict_orders += iter_order

    return strict_orders

def get_all_strict_orders(alternatives, preorder):
    """given a preorder, return all the strict orders consistent with it

    Parameters:
    alternatives (set(int)): all the possible alternatives
    preorder (set((int,int))): a preorder, represented as a set of edges between alternatives

    Returns:
    list(list(int)): strict orders"""

    partial_orders = get_all_partial_orders(alternatives, preorder)
    return partial2strict(partial_orders)