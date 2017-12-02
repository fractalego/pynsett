import os

from igraph import Graph, plot

from pynsett.auxiliary.rule_utils import repeat_db_rules_n_times
from pynsett.nl import SpacyParser as Parser
from parvusdb import GraphDatabase, create_graph_from_string, convert_graph_to_string

_path = os.path.dirname(__file__)


def _create_graph_from_natural_language(sentence):
    g = Graph(directed=True)
    db = GraphDatabase(g)
    parser = Parser(db)
    db = parser.execute(sentence)

    n = 5
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/verbs.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/names.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/adjectives.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/delete.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/subordinates.parvus')).read(), n)
    return db.get_graph()


class Drs:
    def __init__(self, g):
        if not isinstance(g, Graph):
            raise TypeError("Drs needs an igraph.Graph as an argument")
        self._g = g

    def __str__(self):
        return convert_graph_to_string(self._g)

    @staticmethod
    def create_from_natural_language(sentence):
        return Drs(_create_graph_from_natural_language(sentence))

    @staticmethod
    def create_from_predicates_string(string):
        return Drs(create_graph_from_string(string))

    @staticmethod
    def create_empty():
        return Drs(Graph(directed=True))

    def plot(self):
        import copy
        g = copy.deepcopy(self._g)
        g.vs['label'] = g.vs['compound']
        g.es['label'] = g.es['type']
        plot(g)

    def copy(self):
        return Drs(self._g.as_directed())

    def visit(self, function):
        return function.apply(self._g)
