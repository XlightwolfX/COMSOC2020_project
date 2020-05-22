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

def generate_graphs(num_voters, num_graphs, gtype='scale-free', seed=42, params = dict()):
    if 'clique_size' in params.keys():
        assert num_voters % params['clique_size'] == 0, f"Cliques must be of equal size: number of voters must be a multiple \
        of clique_size size. Values passed: num_voters={num_voters}, clique_size={params['clique_size']}"

    gtypes = {
        'scale-free': lambda : nx.DiGraph(nx.scale_free_graph(num_voters, seed=seed)),
        'path': lambda : nx.DiGraph((nx.generators.classic.path_graph(num_voters, create_using = nx.classes.multidigraph.MultiDiGraph))),
        'random': lambda : random_network(num_voters, params['prob'], seed = seed),
        'regular' : lambda : nx.to_directed(nx.generators.random_graphs.random_regular_graph(params['degree'], num_voters, seed)),
        'small-world': lambda : nx.to_directed(nx.generators.random_graphs.watts_strogatz_graph(num_voters, params['degree'], params['prob'], seed)),
        'caveman': lambda : nx.to_directed(nx.generators.community.connected_caveman_graph(num_voters // params['clique_size'], params['clique_size'])),
        }

    if gtype not in gtypes:
        raise NotImplementedError('This graph type has not been implemented.')

    g_func = gtypes[gtype]

    for i in range(num_graphs):
        seed = seed + 1 if seed is not None else None
        yield g_func()