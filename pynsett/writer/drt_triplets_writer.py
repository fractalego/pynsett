import logging

from igraph import Graph
from more_itertools import unique_everseen
from .base_writer import BaseWriter


class DRTTripletsWriter(BaseWriter):
    _logger = logging.getLogger(__name__)

    def visit(self, g):
        triplets = self.__get_relations_and_entities_from_graph(g)
        return triplets

    def __get_relations_and_entities_from_graph(self, g):
        if not isinstance(g, Graph):
            raise TypeError("The writer needs an igraph.Graph as an argument")

        triplets = []
        for edge in g.es:
            from_node = g.vs[edge.tuple[0]]['word']
            to_node = g.vs[edge.tuple[1]]['word']
            relation = edge['type']
            triplets.append((from_node, relation, to_node))

        return list(unique_everseen(triplets, key=tuple))
