import os
import numpy as np

from gensim.models import KeyedVectors


class Metric:
    _substitution_dict = {}
    _path = os.path.dirname(__file__)

    _filename = '../../data/glove.6B.50d.txt'
    _model = KeyedVectors.load_word2vec_format(os.path.join(_path, _filename))

    def similarity(self, lhs, rhs):
        if lhs not in self._substitution_dict:
            return np.linalg.norm(self.__get_vector(lhs) - self.__get_vector(rhs))
        lst = self._substitution_dict[lhs]
        distance_lst = [np.linalg.norm(self.__get_vector(item) - self.__get_vector(rhs)) for item in lst]
        return min(distance_lst)

    def add_substitution(self, name, lst):
        self._substitution_dict[name] = lst

    # Private

    def __get_vector(self, word):
        try:
            return self._model[word]
        except:
            return self._model['entity']
