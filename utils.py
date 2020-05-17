import networkx as nx

def regret(winner, preferences, counts):
    regret = []
    assert len(preferences) == len(counts)

    for preference, count in zip(preferences, counts):
        assert winner in preference
        regret += [preference.index(winner)] * count

    return sum(regret) * 1. / len(regret)

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
