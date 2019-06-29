import logging

from igraph import Graph
from more_itertools import unique_everseen
from parvusdb import GraphDatabase
from .base_writer import BaseWriter


class RelationTripletsWriter(BaseWriter):
    _logger = logging.getLogger(__name__)

    def visit(self, g):
        triplets = self.__get_relations_and_entities_from_graph(g)
        return triplets

    def __get_relations_and_entities_from_graph(self, g):
        if not isinstance(g, Graph):
            raise TypeError("The writer needs an igraph.Graph as an argument")

        db = GraphDatabase(g)
        lst = db.query("MATCH {}(a), {'type': 'relation', 'name': 'r'}(a,b), {}(b) RETURN a, b, r", repeat_n_times=5)
        triplets = [(self.__get_correct_name(item['a'], g),
                     item['r']['text'],
                     self.__get_correct_name(item['b'], g))
                    for item in lst]
        return list(unique_everseen(triplets, key=tuple))

    def __get_correct_name(self, node, g):
        coreferent_name = node['refers_to']
        if not coreferent_name:
            return node['compound']
        return '|'.join(coreferent_name)