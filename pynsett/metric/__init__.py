import os
import numpy as np

from gensim.models import KeyedVectors


class MetricBase(object):
    _substitution_dict = {}

    def similarity(self, lhs, rhs):
        rhs_vector = self._get_vector(rhs)
        if lhs not in self._substitution_dict:
            lhs_vector = self._get_vector(lhs)
            return np.dot(lhs_vector, rhs_vector) / np.linalg.norm(lhs_vector) / np.linalg.norm(rhs_vector)
        candidates_list = self._substitution_dict[lhs]
        distance_list = []
        for item in candidates_list:
            lhs_vector = self._get_vector(item)
            distance = np.dot(lhs_vector, rhs_vector) / np.linalg.norm(lhs_vector) / np.linalg.norm(rhs_vector)
            distance_list.append(distance)
        return max(distance_list)

    def add_substitution(self, name, lst):
        self._substitution_dict[name] = lst

    def _get_vector(self, word):
        return np.array([0.] * 50)


class GloveMetric(MetricBase):
    def __init__(self):
        self._path = os.path.dirname(__file__)
        self._filename = '../data/glove.6B.50d.txt'
        self._model = KeyedVectors.load_word2vec_format(os.path.join(self._path, self._filename))

    def _get_vector(self, word):
        try:
            return self._model[word]
        except:
            return self._model['entity']


class SpacyMetric(MetricBase):
    def __init__(self):
        import spacy

        self._parser = spacy.load('en_core_web_lg')
        self._vocab = self._parser.vocab

    def _get_vector(self, word):
        try:
            return self._vocab[word].vector
        except:
            return self._vocab['entity'].vector


class MetricFactory:
    @staticmethod
    def get_best_available_metric():
        try:
            return SpacyMetric()
        except:
            return GloveMetric()
