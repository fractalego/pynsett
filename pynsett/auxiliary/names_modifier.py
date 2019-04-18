import logging

_logger = logging.getLogger(__file__)


class SentenceNamesModifier:
    def __init__(self, sentence_index):
        self._sentence_index = sentence_index

    def apply(self, g):
        for v in g.vs:
            old_name = v['name']
            new_name = str(self._sentence_index) + old_name
            v['name'] = new_name
