import logging
import os

from igraph import Graph, plot

from pynsett.auxiliary.rule_utils import repeat_db_rules_n_times
from pynsett.nl import SpacyParser as Parser
from parvusdb import GraphDatabase, create_graph_from_string, convert_graph_to_string

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


def _create_graph_from_natural_language(sentence):
    g = Graph(directed=True)
    db = GraphDatabase(g)
    parser = Parser(db)
    parsed_dict = parser.execute(sentence)
    db = parsed_dict['graph']

    n = 5
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/verbs.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/names.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/adjectives.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/delete.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/subordinates.parvus')).read(), n)
    return {'graph': db.get_graph(),
            'name_word_pairs': parsed_dict['name_word_pairs'],
            }


class Drs:

    def __init__(self, g, name_word_pairs=None):
        if not isinstance(g, Graph):
            raise TypeError("Drs needs an igraph.Graph as an argument")
        self._g = g
        if name_word_pairs:
            self._name_word_pairs = name_word_pairs
        elif self._g.vs:
            try:
                self._name_word_pairs = [(v['name'], v['word']) for v in self._g.vs]
            except KeyError as e:
                _logger.warning(str(e))

    def __str__(self):
        return convert_graph_to_string(self._g)

    @property
    def name_word_pairs(self):
        return self._name_word_pairs

    @staticmethod
    def create_from_natural_language(sentence):
        parsed_dict = _create_graph_from_natural_language(sentence)
        return Drs(parsed_dict['graph'], parsed_dict['name_word_pairs'])

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
        return Drs(g=self._g.as_directed())

    def visit(self, function):
        return function.apply(self._g)
