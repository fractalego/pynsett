from nlulite.drt import Drs
from nlulite.drt import DrtGraph
from nlulite.drt import create_graph_from_drs
from nlulite.match import Match
from nlulite.auxiliary import tag_is_noun, tag_is_verb, tag_is_cardinal
import random


def add_unique_names(clause, number):
    unique_string = '_' + str(number)
    for vertex in clause.consequence.graph.g.vs:
        vertex['name'] += unique_string
    for vertex in clause.hypothesis.graph.g.vs:
        vertex['name'] += unique_string
    return clause


class BaseBackwardInference:
    def compute(self):
        return None


class BackwardInference(BaseBackwardInference):
    def __init__(self, data, knowledge):
        self.data = data
        self.knowledge = knowledge
        self.MAX_RECURSION = 500

    def __apply_clause_to_drs(self, clause, data):
        drs = Drs(DrtGraph.create_from_graph(data.graph.g))
        match = Match()
        gdata = drs
        gcons = clause.hypothesis
        ghyp = clause.consequence
        is_match = match.check_sub_isomorphism(gdata, ghyp)
        mgu = match.get_latest_mgu()
        distance = match.get_total_distance()
        if is_match:
            for data_vertex in gdata.graph.g.vs:
                tag = data_vertex["tag"]
                if not tag == "IN":
                    continue
                to_delete = True
                for neighbor_index in gdata.graph.g.neighbors(data_vertex["name"], mode="out"):
                    neighbour = gdata.graph.g.vs[neighbor_index]["name"]
                    try:
                        index = [pair[0] for pair in mgu].index(neighbour)
                    except:
                        to_delete = False
                        break
                if to_delete:
                    data_vertex["word"] = "DELETE"
            for data_vertex in gdata.graph.g.vs:
                for cons_vertex in gcons.graph.g.vs:
                    pair = (data_vertex["name"], cons_vertex["name"])
                    try:
                        pair_is_found = mgu.index(pair) != -1
                        if pair_is_found:
                            data_vertex["name"] = cons_vertex["name"]
                            tag = data_vertex["tag"]
                            if (tag_is_noun(tag) or tag_is_verb(tag) or tag_is_cardinal(tag)):
                                data_vertex["word"] = "DELETE"
                    except Exception as e:
                        continue

            line = gdata.get_string() + "," + gcons.get_string()
            new_drs = Drs(create_graph_from_drs(line))
            new_drs.graph.g.delete_vertices(new_drs.graph.g.vs.select(word_eq="DELETE"))
            drs.graph.g = new_drs.graph.g

        names_dict = match.get_name_substitution_dict()
        label_dict = match.get_label_substitution_dict()
        for vertex in drs.graph.g.vs:
            name = vertex['name']
            word = vertex['word']
            try:
                substitute_word = names_dict[name]
                substitute_label = label_dict[name]
                if word == '[*]':
                    vertex['word'] = substitute_word
                    vertex['label'] = substitute_label
                if word.find('|') != -1 and substitute_word in word.split('|'):
                    vertex['word'] = substitute_word
                    vertex['label'] = substitute_label
            except Exception as e:
                continue
        return drs, distance

    def compute(self):
        data = self.data
        tot_distance = 0
        for i in range(self.MAX_RECURSION):
            clauses = self.knowledge.ask_rule_bw(data)
            result_pairs = []
            for clause_pair in clauses:
                clause = clause_pair[0]
                clause_weight = clause_pair[1]
                clause = add_unique_names(clause, random.randint(0, 1000))
                drs, w = self.__apply_clause_to_drs(clause, data)
                if w > 0:
                    result_pairs.append((drs, w * clause_weight))
            if len(result_pairs) == 0:
                break
            result_pairs = sorted(result_pairs, key=lambda x: -x[1])
            data = result_pairs[0][0]
            tot_distance += result_pairs[0][1]
        return data, tot_distance


class PipelinedBackwardInference(BaseBackwardInference):
    def __init__(self, data, knowledge):
        self.data = data
        self.knowledge = knowledge
        self.tot_distance = 0

    def compute(self):
        tot_distance = 0
        data = self.data
        for knowledge_set in self.knowledge:
            inference = BackwardInference(data, knowledge_set)
            end_drs, distance = inference.compute()
            data = end_drs
            tot_distance += distance
        return data, tot_distance
