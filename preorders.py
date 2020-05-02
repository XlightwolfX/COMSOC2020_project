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

def partial2strict(partial_order):
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

def get_all_strict_orders(alternatives, preorder):
    """given a preorder, return all the strict orders consistent with it

    Parameters:
    alternatives (set(int)): all the possible alternatives
    preorder (set((int,int))): a preorder, represented as a set of edges between alternatives

    Returns:
    list(list(int)): strict orders"""

    partial_orders = get_all_partial_orders(alternatives, preorder)
    strict_orders = []
    # for each partial order, get the consistent orders
    for partial_order in partial_orders:
        strict_orders += partial2strict(partial_order)

    return strict_orders