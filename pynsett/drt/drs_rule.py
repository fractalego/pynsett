from igraph import Graph
from parvusdb import GraphDatabase
from parvusdb.utils.code_container import DummyCodeContainerFactory

from .node_matcher import VectorNodeMatcher

class DrsRule:
    def __init__(self, text, metric, matching_variables):
        self.text = text
        self.text += " RETURN %s;" % ','.join(matching_variables)
        self.metric = metric

    def test(self):
        g = Graph(directed=True)
        self.visit(g)

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g,
                           node_matcher=VectorNodeMatcher(self.metric),
                           code_container_factory=DummyCodeContainerFactory())
        lst = db.query(str(self.text), repeat_n_times=5)
        if lst:
            return True
        return False

    def __str__(self):
        return self.text
