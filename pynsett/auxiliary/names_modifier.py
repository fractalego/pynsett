import logging

_logger = logging.getLogger(__file__)


class DiscourseNamesModifier:
    def __init__(self, index):
        self._index = index

    def visit(self, g):
        for item in g.vs:
            item['name'] = str(self._index) + item['name']
        for item in g.es:
            item['name'] = str(self._index) + item['name']


class SentenceNamesModifier:
    def __init__(self, sentence_index):
        self._sentence_index = sentence_index

    def visit(self, g):
        assign_proper_index_to_nodes_names(g.vs, self._sentence_index)


def assign_proper_index_to_nodes_names(nodes, index):
    for item in nodes:
        if _needs_to_be_made_unique(item['name']):
            item['name'] = str(index) + item['name']
    return nodes


def _needs_to_be_made_unique(name):
    if name[0] == 'v':
        return True
    return False
