import logging

_logger = logging.getLogger(__name__)


def find_weight_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return 1


def clean_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        new_s = s[:start - 1] + s[end + 1:]
        return new_s
    except ValueError:
        return s


def eliminate_spaces(line):
    line = line.replace(' ', '')
    line = line.replace('\t', '')
    line = line.replace('\n', '')
    return line


class UniqueNamesModifier:
    def visit(self, g):
        from ..auxiliary import get_random_name
        for v in g.vs:
            random_name = get_random_name()
            old_name = v['name']
            new_name = old_name + random_name
            v['name'] = new_name
        for e in g.es:
            e['name'] += get_random_name()


class BaseForwardInference:
    def compute(self):
        return None


class ForwardInference(BaseForwardInference):
    _unique = UniqueNamesModifier()

    def __init__(self, data, knowledge):
        self.data = data
        self.knowledge = knowledge
        self.MAX_DATA_LENGTH = 10

    def __apply_clause_to_drs(self, rule, data):
        drs = data.copy()
        drs.apply(self._unique)
        is_match = drs.apply(rule)
        distance = 1
        if not is_match:
            distance = 0
        return drs, distance

    def compute(self):
        '''
        Applies all the rules to a drs
        :return: all the variants of the drs after a rule match as a pair (<NEW_DRS>, <WEIGHT>)
        '''

        data = self.data
        clauses = self.knowledge.ask_rule(data)
        result_pairs = []
        for clause_pair in clauses:
            clause = clause_pair[0]
            clause_weight = clause_pair[1]
            drs, w = self.__apply_clause_to_drs(clause, data)
            if w > 0:
                result_pairs.append((drs, w * clause_weight))
        result_pairs = sorted(result_pairs, key=lambda x: -x[1])
        return result_pairs


class ForwardInferenceChain(BaseForwardInference):
    def __init__(self, data, knowledge):
        self.data = data
        self.knowledge = knowledge

    def compute(self):
        data = self.data
        tot_distance = 0
        for knowledge_set in self.knowledge:
            inference = ForwardInference(data, knowledge_set)
            end_drs, distance = inference.compute()
            data = end_drs
            tot_distance += distance
        return data, tot_distance
