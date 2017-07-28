import os
import sys
import numpy as np

from gensim.models import KeyedVectors

_path = os.path.dirname(__file__)

_filename = '../../data/glove.6B.50d.txt'
_model = KeyedVectors.load_word2vec_format(os.path.join(_path, _filename))

class Metric:

    def similarity(self, lhs, rhs):
        return np.linalg.norm(self.__get_vector(lhs) - self.__get_vector(rhs))

    def __get_vector(self, word):
        try:
            return _model[word]
        except:
            return _model['entity']
