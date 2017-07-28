from more_itertools import unique_everseen


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
    def apply(self, g):
        from ..auxiliary import get_random_name
        for v in g.vs:
            v['name'] += get_random_name()
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
        self.MAX_RECURSION = 1
        self.MAX_DATA_LENGTH = 10

    def __apply_clause_to_drs(self, rule, data):
        drs = data.copy()
        drs.visit(self._unique)
        is_match = drs.visit(rule)
        distance = 1
        if not is_match:
            distance = 0
        return drs, distance

    def compute(self):
        data = self.data
        tot_distance = 0
        for i in range(self.MAX_RECURSION):
            clauses = self.knowledge.ask_rule(data)
            result_pairs = []
            for clause_pair in clauses:
                clause = clause_pair[0]
                clause_weight = clause_pair[1]
                drs, w = self.__apply_clause_to_drs(clause, data)
                if w > 0:
                    result_pairs.append((drs, w * clause_weight))
            if len(result_pairs) == 0:
                break
            result_pairs = sorted(result_pairs, key=lambda x: -x[1])
            data = result_pairs[0][0]
            tot_distance += result_pairs[0][1]
        return data, tot_distance

    def __compute_for_single_data_with_a_star(self, data, all_data, tot_distance):
        for i in range(self.MAX_RECURSION):
            clauses = self.knowledge.ask_rule_fw(data)
            result_pairs = []
            for clause_pair in clauses:
                clause = clause_pair[0]
                clause_weight = clause_pair[1]
                drs, w = self.__apply_clause_to_drs(clause, data)
                if w > 0:
                    result_pairs.append((drs, w * clause_weight + tot_distance))
            if len(result_pairs) != 0:
                all_data += result_pairs
            all_data = sorted(all_data, key=lambda x: -x[1])
            data = all_data[0][0]
            tot_distance += all_data[0][1]
        return_data = sorted(all_data, key=lambda x: -x[1])
        if len(return_data) > self.MAX_DATA_LENGTH:
            return_data = return_data[0:5]
        return return_data

    def compute_with_a_star(self, all_data=None):
        data = self.data
        tot_distance = 0
        if all_data == None:
            all_data = [(data, 0)]
        return_data = self.__compute_for_single_data_with_a_star(data, all_data, tot_distance)
        return return_data

    def __compute_for_single_data(self, data, tot_distance):
        clauses = self.knowledge.ask_rule(data)
        result_pairs = []
        for clause_pair in clauses:
            clause = clause_pair[0]
            clause_weight = clause_pair[1]
            drs, w = self.__apply_clause_to_drs(clause, data)
            if w > 0:
                result_pairs.append([drs, w * clause_weight])
        for i in range(len(result_pairs)):
            result_pairs[i][1] += tot_distance
        return result_pairs

    def compute_with_static_models_semantics(self, all_data=None):
        data = self.data
        if all_data == None:
            all_data = [[data, 0]]
        return_data = all_data
        for i in range(self.MAX_RECURSION):
            all_data = return_data
            for drs, w in all_data:
                data_and_weights = self.__compute_for_single_data(drs, w)
                return_data += data_and_weights
        return return_data


class PipelinedForwardInference(BaseForwardInference):
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

    def compute_with_a_star(self):
        tot_distance = 0
        data = self.data
        all_data = [(self.data, tot_distance)]
        for knowledge_set in self.knowledge:
            inference = ForwardInference(data, knowledge_set)
            all_data = inference.compute_with_a_star(all_data)
            all_data = sorted(all_data, key=lambda x: -x[1])
        if len(all_data) > 0:
            data = all_data[0][0]
            tot_distance += all_data[0][1]
        return all_data

    def compute_with_static_models_semantics(self):
        tot_distance = 0
        data = self.data
        all_data = [(self.data, tot_distance)]
        for knowledge_set in self.knowledge:
            inference = ForwardInference(data, knowledge_set)
            all_data = inference.compute_with_static_models_semantics(all_data)
        all_data = list(unique_everseen(all_data))
        return all_data
