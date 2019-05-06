from igraph import Graph
from parvusdb import GraphDatabase
from .node_matcher import VectorNodeMatcher


class DrsMatcher:
    def __init__(self, small_drs, metric):
        self.small_drs = small_drs
        self.metric = metric

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g, node_matcher=VectorNodeMatcher(self.metric))
        rule = 'MATCH ' + str(self.small_drs) + ' RETURN __RESULT__;'
        lst = db.query(rule)
        return lst
