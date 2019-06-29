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

    n = 10
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/verbs.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/names.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/various.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/prepositions.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/punctuation.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/compound1.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/compound2.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/adjectives.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/delete.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/subordinates.parvus')).read(), n)
    db = repeat_db_rules_n_times(db, open(os.path.join(_path, '../rules/parsing/recursive.parvus')).read(), n)
    return {'graph': db.get_graph(),
            'word_nodes': parsed_dict['word_nodes'],
            }


def _get_union_of_graphs(graph_list):
    g = Graph(directed=True)
    db = GraphDatabase(g)
    query = ""
    for g in graph_list:
        query += f" CREATE {convert_graph_to_string(g)}"
    db.query(query)
    return db.get_graph()


class Drs:
    def __init__(self, g, word_nodes=None):
        if not isinstance(g, Graph):
            raise TypeError("Drs needs an igraph.Graph as an argument")
        self._g = g
        if word_nodes:
            self._word_nodes = word_nodes
        elif self._g.vs:
            try:
                self._word_nodes = [(v['name'], v['word']) for v in self._g.vs]
            except KeyError as e:
                _logger.warning(str(e))

    def __str__(self):
        return convert_graph_to_string(self._g)

    @property
    def word_nodes(self):
        return self._word_nodes

    @staticmethod
    def create_union_from_list_of_drs(drs_list):
        return Drs(_get_union_of_graphs([drs._g for drs in drs_list]))

    @staticmethod
    def create_from_natural_language(sentence):
        parsed_dict = _create_graph_from_natural_language(sentence)
        return Drs(parsed_dict['graph'], parsed_dict['word_nodes'])

    @staticmethod
    def create_from_predicates_string(string):
        return Drs(create_graph_from_string(string))

    @staticmethod
    def create_empty():
        return Drs(Graph(directed=True))

    def plot(self):
        import copy
        g = copy.deepcopy(self._g)
        g.vs['label'] = [v['compound'] + ': ' + v['entity'] for v in g.vs]
        g.es['label'] = g.es['type']
        plot(g, bbox=(0, 0, 1200, 1200))

    def copy(self):
        return Drs(g=self._g.as_directed())

    def apply(self, function):
        return function.visit(self._g)
