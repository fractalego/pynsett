import logging
import os

from igraph import Graph
from parvusdb import GraphDatabase

from pynsett.auxiliary.rule_utils import repeat_db_rules_n_times

_path = os.path.dirname(__file__)


class SingleSentenceAnaphoraVisitor:
    __logger = logging.getLogger(__name__)

    def __init__(self):
        self._rules = open(os.path.join(_path, '../rules/intra_sentence_anaphora.parvus')).read()

    def apply(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.apply_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g)
        lst = db.query(self._rules, repeat_n_times=1)
        return lst


class InterSentenceAnaphoraVisitor:
    __logger = logging.getLogger(__name__)

    def __init__(self, num_sentences):
        self._rules = open(os.path.join(_path, '../rules/inter_sentence_anaphora.parvus')).read()
        self._times_to_repeat_rules = num_sentences - 1

    def apply(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.apply_to_graph() needs an igraph.Graph as an argument")
        db = GraphDatabase(g)
        lst = db.query(self._rules, repeat_n_times=self._times_to_repeat_rules)
        return lst
