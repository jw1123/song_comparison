#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from matplotlib.pyplot import show
from os import path


class Graphdist:

    def __init__(self, song_collection, distance_collection):
        self.so = song_collection
        self.di = distance_collection
        self.savegraph()

    def savegraph(self):

        G = nx.DiGraph()
        # Iterate through all songs and create nodes
        # of them in the graph
        for s in self.so.find():
            G.add_node(s['song_id'], s['metadata'])
        # Iterate through all distances and create
        # edges between the songs of the graph
        for d in self.di.find():
            # Multiply the weight by 10000 because the values
            # are rounded up in Gephi
            G.add_edge(d['source'], d['target'], weight=10000*d['weight'])
        # Create the GraphML file
        nx.write_graphml(G, path.dirname(path.realpath("graph.py"))
                                        + '/song_comparison.graphml')
