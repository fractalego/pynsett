import logging
import os

from igraph import Graph
from parvusdb import GraphDatabase

_path = os.path.dirname(__file__)


class GraphJoinerVisitor:
    __logger = logging.getLogger(__name__)

    def __init__(self, drs):
        self._rules = """
        CREATE %s;
        """ % str(drs)

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g)
        lst = db.query(self._rules, repeat_n_times=1)
        return lst


class SentenceJoinerVisitor:
    __logger = logging.getLogger(__name__)

    def __init__(self, from_sentence, to_sentence):
        self._rules = """
        MATCH {'is_head_token': '%s'}(a), {'is_head_token': '%s'}(b)
        CREATE {}(a), {'type': 'NEXT_SENTENCE'}(a,b), {}(b);
        """ % (str(from_sentence), str(to_sentence))

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g)
        lst = db.query(self._rules, repeat_n_times=1)
        return lst


class CoreferenceJoinerVisitor:
    __logger = logging.getLogger(__name__)


    def __init__(self):
        self._rules = """
        MATCH {'refers_to': %s}(a), {'refers_to': %s}(b)
        CREATE {}(a), {'type': 'REFERS_TO'}(a,b), {}(b)
        CREATE {}(a), {'type': 'REFERS_TO'}(b,a), {}(b);
        """


    def visit(self, g):
        parsed_before = []
        db = GraphDatabase(g)
        for v in g.vs:
            refers_to = v['refers_to']
            if refers_to and refers_to not in parsed_before:
                db.query(self._rules % (str(refers_to), str(refers_to)), repeat_n_times=1)
                parsed_before.append(refers_to)

        return True
