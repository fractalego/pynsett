import logging

from igraph import Graph
from more_itertools import unique_everseen
from .base_writer import BaseWriter


class DRTTripletsWriter(BaseWriter):
    _logger = logging.getLogger(__name__)

    def visit(self, g):
        triplets = self.__get_relations_and_entities_from_graph(g)
        return triplets

    def __get_relations_and_entities_from_graph(self, g):
        if not isinstance(g, Graph):
            raise TypeError("The writer needs an igraph.Graph as an argument")

        data = {'nodes': [], 'edges': []}
        for edge in g.es:
            from_node = g.vs[edge.tuple[0]]
            to_node = g.vs[edge.tuple[1]]
            relation = edge
            data['nodes'].append({'id': from_node['name'], 'label': self.__get_correct_name(from_node)})
            data['nodes'].append({'id': to_node['name'], 'label': self.__get_correct_name(to_node)})
            data['edges'].append({'from': from_node['name'], 'to': to_node['name'], 'label': relation['type'],
                                  'arrows': 'to'})

        data['nodes'] = list(unique_everseen(data['nodes'], key=dict))
        data['edges'] = list(unique_everseen(data['edges'], key=dict))
        return data

    def __get_correct_name(self, node):
        coreferent_name = node['refers_to']
        if not coreferent_name:
            return node['compound']
        return '|'.join(coreferent_name)