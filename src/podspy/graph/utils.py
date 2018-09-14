#!/usr/bin/env python3


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"


def get_edges(src, target, collection):
    edges = set()

    for e in collection:
        if e.src == src and e.target == target:
            edges.add(e)

    return frozenset(edges)
