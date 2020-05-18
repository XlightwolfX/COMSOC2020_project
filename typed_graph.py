import random
from voter import Voter
from partialorders import PartialOrder

def voter_type(i):
    return [1,2,3,4] if i % 2 == 0 else [2,1,3,4]

def cotyped(i, j):
    return type(i) == type(j)

def generate_typed_graph(N = 50):
    # generate a graph where the voters have two types
    id2voter = dict()
    for i in range(N):
        strict = voter_type(i)
        # second parameter is indecisivness, i put these arbitrary probabilities
        partial = PartialOrder.generate_from_strict(strict, random.choice([0] + [0.2] * 4 + [1] * 8))
        voter = Voter(partial, strict)
        id2voter[i] = voter

    # random graph
    graph = dict()
    for i in range(N):
        graph[i] = []
        for j in range(N):
            if i != j:
                thresh = 0.5 # 0.7 if cotyped(i, j) else 0.3
                if random.random() <= thresh:
                    graph[i].append(j)

    return id2voter, graph