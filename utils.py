import networkx as nx
from partialorders import PartialOrder


def regret(winner, preferences, counts):
    regret = []
    assert len(preferences) == len(counts)

    for preference, count in zip(preferences, counts):
        assert winner in preference
        regret += [preference.index(winner)] * count

    return sum(regret) * 1. / len(regret)


def partial_regret(winner, voters):
    # compute average partial regret, that is, per each
    # voter number of alternatives that are preferred to the winner
    p_regret = []

    for voter in voters:
        p_regret.append(sum((1 for i, j in voter.partial.edges if j == winner)))

    return sum(p_regret) * 1. / len(p_regret)


def ind_levels(N):
    # function that we will use to get the edges from a dictionary-graph
    get_edges = lambda graph: {(i, j) for i in graph.keys() for j in graph[i]}

    # will contain all indifference levels
    all_levels = set()

    # [1,2,3,...N]
    strict = list(range(1, N+1))
    # strict order represented as a transitive graph
    graph = PartialOrder(strict).partial

    # recursive function used to actually computed the values
    # this will populate "all_levels"
    def aux(graph):
        all_levels.add(PartialOrder(graph).compute_indecisivness())

        edges = get_edges(graph)

        # for all edges, drop this edge and
        # compute recursevly indecision on the obtained graph
        for edge in edges:
            new_partial = {i: [] for i in graph.keys()}
            for edge_prime in edges:
                if edge != edge_prime:
                    i, j = edge_prime
                    new_partial[i].append(j)
            aux(new_partial)

    # populate all_levels
    aux(graph)

    # return result, as a nice sorted list
    return sorted(all_levels)


def get_dag_edit_distance(graph1, graph2, optim=False):
    """
    Calculate graph edit distance: minimum sequence of node and edge operations
    for graph1 and graph2 to become isomorphic.
    graph1, graph2 [PartialOrder]
    optim [bool] - if TRUE then use approximation algorithm of GED
    """
    G1 = nx.DiGraph(graph1.partial)
    G2 = nx.DiGraph(graph2.partial)

    dist = 0.0
    if optim:
        for i in nx.algorithms.similarity.optimize_graph_edit_distance(G1, G2):
            dist = i
    else:
        dist = nx.algorithms.similarity.graph_edit_distance(G1, G2)

    return dist
