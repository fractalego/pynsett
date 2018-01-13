import logging

from nltk.tokenize import sent_tokenize

from pynsett.discourse.anaphora import SingleSentenceAnaphoraVisitor, InterSentenceAnaphoraVisitor
from pynsett.discourse.global_graph_visitors import GraphJoinerVisitor, SentenceJoinerVisitor
from pynsett.discourse.single_tokens_visitors import HeadTokenVisitor
from pynsett.inference.forward_inference import UniqueNamesModifier
from ..drt import Drs


class Discourse:
    _logger = logging.getLogger(__name__)
    _single_sentence_anaphora_visitor = SingleSentenceAnaphoraVisitor()
    _unique = UniqueNamesModifier()
    _discourse = Drs.create_empty()
    _drs_list = []

    def __init__(self, text):
        text = self.__sanitize_text(text)
        self._sentences_list = sent_tokenize(text)
        for sentence_index, sentence in enumerate(self._sentences_list):
            try:
                if sentence == '.':
                    continue
                drs = Drs.create_from_natural_language(sentence)
                drs.visit(self._single_sentence_anaphora_visitor)
                drs.visit(HeadTokenVisitor(sentence_index))
                self._drs_list.append(drs)
            except Exception as e:
                self._logger.warning('Exception caught in Discourse: ' + str(e))
        if len(self._sentences_list) == 1:
            self._discourse = self._drs_list[0]
            return
        for drs in self._drs_list:
            drs.visit(self._unique)
            self._discourse.visit(GraphJoinerVisitor(drs))
        for sentence_index in range(len(self._sentences_list) - 1):
            self._discourse.visit(SentenceJoinerVisitor(sentence_index, sentence_index + 1))
        self._discourse.visit(InterSentenceAnaphoraVisitor(len(self._sentences_list)))

    # Private

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
