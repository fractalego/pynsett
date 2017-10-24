from igraph import Graph
from parvusdb import GraphDatabase
from .base_writer import BaseWriter


class RelationTripletsWriter(BaseWriter):
    def _get_relations_and_entities_from_graph(self, g):
        if not isinstance(g, Graph):
            raise TypeError("The writer needs an igraph.Graph as an argument")

        db = GraphDatabase(g)
        lst = db.query("MATCH {}(a), {'type': 'relation', 'name': 'r'}(a,b), {}(b) RETURN a, b, r",
                       repeat_n_times=1)
        triplets = [(item['a']['compound'], item['r']['text'], item['b']['compound']) for item in lst]
        return triplets

    def apply(self, g):
        triplets = self._get_relations_and_entities_from_graph(g)
        return triplets
