import logging

from nltk.tokenize import sent_tokenize

from pynsett.auxiliary.names_modifier import SentenceNamesModifier
from pynsett.discourse.anaphora import AllenCoreferenceVisitorsFactory
from pynsett.discourse.global_graph_visitors import GraphJoinerVisitor, SentenceJoinerVisitor
from pynsett.discourse.single_tokens_visitors import HeadTokenVisitor
from ..drt import Drs


class Discourse:
    _logger = logging.getLogger(__name__)

    def __init__(self, text):
        self._discourse = Drs.create_empty()
        self._drs_list = []

        text = self.__sanitize_text(text)
        self._sentences_list = sent_tokenize(text)
        name_word_pairs = []
        for sentence_index, sentence in enumerate(self._sentences_list):
            try:
                if sentence == '.':
                    continue
                drs = Drs.create_from_natural_language(sentence)
                name_word_pairs += [(str(sentence_index) + n, w) for n, w in drs.name_word_pairs]
                drs.visit(HeadTokenVisitor(sentence_index))
                drs.visit(SentenceNamesModifier(sentence_index))
                self._drs_list.append(drs)
            except Exception as e:
                self._logger.warning('Exception caught in Discourse: ' + str(e))

        coreference_visitor_factory = AllenCoreferenceVisitorsFactory(name_word_pairs)
        for i, drs in enumerate(self._drs_list):
            drs.visit(coreference_visitor_factory.create(i))

        self.__create_discourse_graph()

    # Private
    def __create_discourse_graph(self):
        if len(self._sentences_list) == 1:
            self._discourse = self._drs_list[0]
            return
        for drs in self._drs_list:
            self._discourse.visit(GraphJoinerVisitor(drs))
        for sentence_index in range(len(self._sentences_list) - 1):
            self._discourse.visit(SentenceJoinerVisitor(sentence_index, sentence_index + 1))

    def __sanitize_text(self, text):
        text = text.replace('\n', '.\n')
        text = text.replace('.[', '. [')
        text = text.replace('...', '.')
        text = text.replace('..', '.')
        text = text.replace('\n.', '\n')
        return text

    # Iterator operations

    def __getitem__(self, item):
        return self._sentences_list[item], self._drs_list[item]

    def __len__(self):
        return len(self._sentences_list)

    def get_discourse_drs(self):
        return self._discourse
