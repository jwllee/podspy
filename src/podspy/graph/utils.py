#!/usr/bin/env python3


def get_edges(src, target, collection):
    edges = set()

    for e in collection:
        if e.src == src and e.target == target:
            edges.add(e)

    return frozenset(edges)
