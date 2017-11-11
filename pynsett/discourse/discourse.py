import logging
from nltk.tokenize import sent_tokenize

from pynsett.discourse.anaphora import SingleSentenceAnaphoraVisitor
from ..drt import Drs


class Discourse:
    _logger = logging.getLogger(__name__)
    _single_sentence_anaphora_visitor = SingleSentenceAnaphoraVisitor()

    def __init__(self, text):
        self.drs_list = []
        text = self.__sanitize_text(text)
        self.sentences_list = sent_tokenize(text)
        for sentence_index, sentence in enumerate(self.sentences_list):
            try:
                drs = Drs.create_from_natural_language(sentence)
                drs.visit(self._single_sentence_anaphora_visitor)
                self.drs_list.append(drs)
            except Exception as e:
                self._logger.warning('Exception caught in Discourse: ' + str(e))

    # Private
    def __sanitize_text(self, text):
        text = text.replace('\n', '.\n')
        return text

    # Iterator operations

    def __getitem__(self, item):
        return self.sentences_list[item], self.drs_list[item]

    def __len__(self):
        return len(self.sentences_list)
