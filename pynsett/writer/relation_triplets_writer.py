import logging
from igraph import Graph
from parvusdb import GraphDatabase
from .base_writer import BaseWriter


class RelationTripletsWriter(BaseWriter):
    _logger = logging.getLogger(__name__)

    def apply(self, g):
        triplets = self.__get_relations_and_entities_from_graph(g)
        return triplets

    # Private

    def __get_relations_and_entities_from_graph(self, g):
        if not isinstance(g, Graph):
            raise TypeError("The writer needs an igraph.Graph as an argument")

        db = GraphDatabase(g)
        lst = db.query("MATCH {}(a), {'type': 'relation', 'name': 'r'}(a,b), {}(b) RETURN a, b, r",
                       repeat_n_times=1)
        triplets = [(self.__substitute_node_with_coreferent(item['a'], g)['compound'],
                     item['r']['text'],
                     self.__substitute_node_with_coreferent(item['b'], g)['compound'])
                    for item in lst]
        return triplets

    def __substitute_node_with_coreferent(self, node, g):
        try:
            coreferent_name = node['refers_to']
            if not coreferent_name:
                return node
            return g.vs.find(name=coreferent_name)
        except Exception as e:
            self._logger.warning("While fetching 'refers_to': " + str(e))
            return node
