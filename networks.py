import networkx as nx


def generate_graphs(num_voters, num_graphs, gtype='scale-free', seed=42):
    gtypes = {
        'scale-free': nx.scale_free_graph,
        'path': lambda n, seed: nx.generators.classic.path_graph(n, create_using = nx.classes.multidigraph.MultiDiGraph),
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
