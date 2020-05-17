import networkx as nx
import random

def random_network(n, p, seed):
    random.seed(seed)
    graph = dict()
    for i in range(n):
        graph[i] = []
        for j in range(n):
            if i != j:
                if random.random() <= p:
                    graph[i].append(j)

    return nx.DiGraph(graph)

def generate_graphs(num_voters, num_graphs, gtype='scale-free', seed=42):
    gtypes = {
        'scale-free': nx.scale_free_graph,
        'path': lambda n, seed: nx.generators.classic.path_graph(n, create_using = nx.classes.multidigraph.MultiDiGraph),
        # TODO better control of parameters
        'random': lambda n, seed: random_network(n, 0.5, seed)
        # these dont work but we need something similar
        # 'regular' : lambda n, seed: nx.generators.random_graphs.random_regular_graph(n // 4, n, seed),
        # 'small-world': lambda n, seed : connected_watts_strogatz_graph()
        }

    if gtype not in gtypes:
        raise NotImplementedError('This graph type has not been implemented.')

    g_func = gtypes[gtype]

    for i in range(num_graphs):
        seed = seed + 1 if seed is not None else None
        yield g_func(num_voters, seed=seed)
