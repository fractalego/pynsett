import logging
import os

from igraph import Graph
from parvusdb import GraphDatabase

_path = os.path.dirname(__file__)


class HeadTokenVisitor:
    __logger = logging.getLogger(__name__)

    def __init__(self, sentence_number):
        self._rules = """
        MATCH {'is_head_token': True}(a)
        SET (assoc a "is_head_token" "%s");
        """ % str(sentence_number)

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g)
        lst = db.query(self._rules, repeat_n_times=1)
        return lst
