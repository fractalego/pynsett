import logging
import os

from igraph import Graph
from parvusdb import GraphDatabase
from allennlp.predictors.predictor import Predictor

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


class AllenCoreferenceVisitor:
    def __init__(self, sentence_index, coreference_dict):
        self._sentence_index = sentence_index
        self._coreference_dict = coreference_dict

    def apply(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.apply_to_graph() needs an igraph.Graph as an argument")

        for v in g.vs:
            key = v['name']
            if key in self._coreference_dict:
                v['refers_to'] = self._coreference_dict[key]


class AllenCoreferenceVisitorsFactory:
    def __init__(self, name_word_pairs):
        self._predictor = Predictor.from_path(os.path.join(_path, '../data/coref-model-2018.02.05.tar.gz'))
        self._coreference_dict = self.__create_coreference_dict(name_word_pairs)

    def create(self, sentence_index):
        return AllenCoreferenceVisitor(sentence_index, self._coreference_dict)

    # Private

    def __create_coreference_dict(self, name_word_pairs):
        coreference_dict = {}

        words = [w for _, w in name_word_pairs]
        keys = [n for n, _ in name_word_pairs]
        clusters = self.__predict(words)
        for cluster in clusters:
            cluster_words = ['_'.join(words[s:e + 1]) for s, e in cluster]
            for start, end in cluster:
                if start != end:
                    continue
                coreference_dict[keys[start]] = cluster_words

        return coreference_dict

    def __predict(self, words):
        return self._predictor.predict_tokenized(words)['clusters']

