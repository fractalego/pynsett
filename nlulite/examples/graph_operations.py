from igraph import Graph


class GraphBuilder:
    def __init__(self, g):
        self.g = g
        self.name_substitution_dict = {}

    def add_graph(self, rhs_graph):
        rhs_graph = self.__substitute_names_in_graph(rhs_graph)
        self.g = self.__merge_graphs(self.g, rhs_graph)
        return self

    def with_graph(self, rhs_graph):
        is_match, mapping, _ = self.g.subisomorphic_vf2(other=rhs_graph, return_mapping_12=True)
        if not is_match:
            return self
        for lhs, rhs in enumerate(mapping):
            if rhs == -1:
                continue
            lhs_name = self.g.vs[lhs]['name']
            rhs_name = rhs_graph.vs[rhs]['name']
            self.name_substitution_dict[rhs_name] = lhs_name

    def remove_graph(self, rhs_graph):
        rhs_graph = self.__substitute_names_in_graph(rhs_graph)
        vertices_to_delete = []
        edges_to_delete = []
        for v in rhs_graph.vs:
            vertices_to_delete += self.g.vs.select(**v.attributes())
        for e in rhs_graph.es:
            edges_to_delete += self.g.es.select(**e.attributes())
        for v in vertices_to_delete:
            if len(v.neighbors()) == 1:
                self.g.delete_vertices(v)
        for e in edges_to_delete:
            self.g.delete_edges(e)
        return self

    def add_triplet(self, from_vertex, relation, to_vertex):
        triplet = self.__create_triplet(from_vertex, relation, to_vertex)
        return self.add_graph(triplet)

    def remove_triplet(self, from_vertex, relation, to_vertex):
        triplet = self.__create_triplet(from_vertex, relation, to_vertex)
        return self.remove_graph(triplet)

    def remove_vertex(self, vertex_dict):
        vertex = self.__create_vertex(vertex_dict)
        return self.remove_graph(vertex)

    def remove_edge(self, from_vertex, relation, to_vertex):
        triplet = self.__create_triplet(from_vertex, relation, to_vertex)
        triplet = self.__substitute_names_in_graph(triplet)
        edges_to_delete = []
        for e in triplet.es:
            edges_to_delete += self.g.es.select(**e.attributes())
        for e in edges_to_delete:
            self.g.delete_edges(e)
        return self

    def with_triplet(self, from_vertex, relation, to_vertex):
        triplet = self.__create_triplet(from_vertex, relation, to_vertex)
        self.with_graph(triplet)

    def build(self):
        return self.g

    def build_variables(self, variables):
        variables = set(self.__substitute_names_in_list(variables))
        return [v.attributes() for v in self.g.vs if v['name'] in variables]

    # Private

    def __create_vertex(self, vertex):
        g = Graph()
        g.add_vertex(**vertex)
        return g

    def __create_triplet(self, from_vertex, relation, to_vertex):
        triplet = Graph()
        triplet.add_vertex(**from_vertex)
        triplet.add_vertex(**to_vertex)
        triplet.add_edge(source=from_vertex['name'], target=to_vertex['name'], **relation)
        return triplet

    def __substitute_names_in_graph(self, g):
        for i, v in enumerate(g.vs):
            name = v['name']
            try:
                new_name = self.name_substitution_dict[name]
                g.vs[i]['name'] = new_name
            except:
                pass
        return g

    def __substitute_names_in_list(self, lst):
        for i, v in enumerate(lst):
            name = lst[i]
            try:
                new_name = self.name_substitution_dict[name]
                lst[i] = new_name
            except:
                pass
        return lst

    def __merge_graphs(self, lhs, rhs):
        for v in rhs.vs:
            lhs.add_vertex(**v.attributes())
        for e in rhs.es:
            lhs.add_edge(rhs.vs[e.tuple[0]]['name'],
                         rhs.vs[e.tuple[1]]['name'],
                         **e.attributes())
        mapping = []
        name_to_index_dict = {}
        mapped_index = 0
        for v in lhs.vs:
            name = v['name']
            try:
                mapping.append(name_to_index_dict[name])
            except:
                name_to_index_dict[name] = mapped_index
                mapping.append(mapped_index)
                mapped_index += 1
        lhs.contract_vertices(mapping=mapping, combine_attrs='first')
        return lhs


def convert_graph_to_string(g):
    drt_string = ""
    for vertex in g.vs:
        attributes = vertex.attributes()
        attributes.pop('name')
        drt_string += str(attributes)
        drt_string += '('
        drt_string += vertex['name']
        drt_string += ')'
        drt_string += ', '
    for edge in g.es:
        attributes = edge.attributes()
        drt_string += str(attributes)
        drt_string += '('
        drt_string += g.vs[edge.tuple[0]]['name']
        drt_string += ','
        drt_string += g.vs[edge.tuple[1]]['name']
        drt_string += ')'
        drt_string += ', '
    drt_string = drt_string[:-2]

    return drt_string


def is_edge(string):
    return string.find(',') != -1


def create_graph_from_string(graph_string, directed=True):
    import ast
    g = Graph(directed=directed)
    line = graph_string.replace(' ', '')
    line = line.replace('\n', '')
    predicates_strings = line.split("),")
    vertices_to_add = []
    edges_to_add = []
    for predicate in predicates_strings:
        predicate = predicate.replace(')', '')
        attributes_str, name_str = predicate.split("(")
        attributes_dict = ast.literal_eval(attributes_str)
        if not is_edge(name_str):
            attributes_dict['name'] = name_str
            vertices_to_add.append(attributes_dict)
        else:
            source, target = name_str.split(',')
            edges_to_add.append((source, target, attributes_dict))
    for attributes_dict in vertices_to_add:
        g.add_vertex(**attributes_dict)
    for source, target, attributes_dict in edges_to_add:
        g.add_edge(source, target, **attributes_dict)
    return g


def convert_special_characters_to_spaces(line):
    line = line.replace('\t', ' ')
    line = line.replace('\n', ' ')
    return line


class GraphDatabase:
    def __init__(self, directed=True):
        self.g = Graph(directed=directed)
        self.directed = directed
        self.action_list = ['MATCH', 'CREATE', 'REMOVE', 'RETURN']
        self.action_dict = {'MATCH': self.__match,
                            'CREATE': self.__create,
                            'REMOVE': self.__remove,
                            }

    def query(self, string):
        action_graph_pairs = self.__get_action_graph_pairs_from_query(string)
        builder = GraphBuilder(self.g)
        for action, graph_str in action_graph_pairs:
            if action == 'RETURN':
                return self.__return(graph_str, builder)
            self.action_dict[action](graph_str, builder)

    # Private

    def __get_action_graph_pairs_from_query(self, query):
        import re

        query = convert_special_characters_to_spaces(query)
        graph_list = re.split('|'.join(self.action_list), query)
        query_list_positions = [query.find(graph) for graph in graph_list]
        query_list_positions = query_list_positions
        query_list_positions = query_list_positions
        action_list = [query[query_list_positions[i] + len(graph_list[i]):query_list_positions[i + 1]].strip()
                       for i in range(len(graph_list) - 1)]
        graph_list = graph_list[1:]
        return zip(action_list, graph_list)

    def __match(self, graph_str, builder):
        graph = create_graph_from_string(graph_str)
        builder.with_graph(graph)

    def __create(self, graph_str, builder):
        graph = create_graph_from_string(graph_str)
        builder.add_graph(graph)

    def __remove(self, graph_str, builder):
        graph = create_graph_from_string(graph_str)
        builder.remove_graph(graph)

    def __return(self, graph_str, builder):
        variables = [v for v in graph_str.strip().replace(' ', '').split(',') if v]
        if not variables:
            return [convert_graph_to_string(builder.build())]
        return builder.build_variables(variables)




if __name__ == '__main__':
    g = Graph()
    builder = GraphBuilder(g)
    builder.add_triplet({'name': 'v1', 'tag': 'NN'}, {'type': 'AGENT'}, {'name': '2'})
    builder.add_triplet({'name': 'v1', 'tag': 'NN'}, {'type': 'AGENT2'}, {'name': 'v4', 'tag': 'VBZ'})
    builder.with_triplet({'name': '_v1', 'tag': 'NN'}, {'type': 'AGENT2'}, {'name': '_v2'})
    builder.add_triplet({'name': '_v1', 'tag': 'NN'}, {'type': 'ANOTHER_AGENT'}, {'name': '_v2'})
    builder.remove_triplet({'name': '_v1', 'tag': 'NN'}, {'type': 'AGENT'}, {'name': '_v2'})
    builder.remove_edge({'name': '_v1', 'tag': 'NN'}, {'type': 'AGENT'}, {'name': '_v2'})
    builder.remove_vertex({'name': '_v1', 'tag': 'NN'})
    g = builder.build()
    print(g)
    print(convert_graph_to_string(g))

    g2 = create_graph_from_string(
        "{'tag': 'NN'}(v1), {'tag': None}(2), {'tag': 'VBZ'}(v4), {'type': 'AGENT76'}(v4,v1), {'type': 'ANOTHER_AGENT'}(v1,2)")
    print(g2)
    print(convert_graph_to_string(g2))

    db = GraphDatabase()
    g_str = db.query("""CREATE {'word': 'alberto', 'tag':'NNP'}(a), {'word': 'WRITES'}(a,b), {'word': 'documentation', 'tag':'NN'}(b) RETURN a
    """)
    print(g_str)

    #db.query("""MATCH {'word': 'alberto', 'tag':'NNP'}(a), {'word': 'writes', 'tag'='VBZ'}(a,b), {'word': 'documentation', 'tag':'NN'}(b)
	#    CREATE {'word': 'alberto', 'tag':'NNP'}(a), {'word': 'WRITES'}(a,b), {'word': 'documentation', 'tag':'NN'}(b)
	#    REMOVE {'word': 'writes', 'tag':'VBZ'}(a,b);
	# """)
