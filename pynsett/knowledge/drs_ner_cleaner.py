from igraph import Graph

from pynsett.drt import Drs


class DrsNERCleaner:
    def __init__(self, words_without_entity):
        self._words_without_entity = words_without_entity

    def visit(self, g):
        if not isinstance(g, Graph):
            raise TypeError("DrsRule.visit_to_graph() needs an igraph.Graph as an argument")
        for vertex in g.vs:
            if vertex['word'] in self._words_without_entity:
                vertex['entity'] = ''
        return Drs(g)
