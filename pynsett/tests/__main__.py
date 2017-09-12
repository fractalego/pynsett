import os

from pynsett.drt import Drs
from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.metric import Metric
from pynsett.drt.drs_matcher import DrsMatcher


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

_path = os.path.dirname(__file__)
    
metric = Metric()

class Tests:
    def __print_test_title(self, string):
        print(string, )

    def copula_test(self):
        self.__print_test_title('The verb to be acts as a copula')
        drs = Drs.create_from_natural_language('this is a test')
        expected_drs = Drs.create_from_predicates_string("{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        return is_match

    def passive_test(self):
        self.__print_test_title('Passive sentences are parsed correctly')
        drs = Drs.create_from_natural_language('the rabbit is eaten by me')
        expected_drs = Drs.create_from_predicates_string("{'entity': '', 'compound': 'rabbit', 'word': 'rabbit', 'tag': 'n'}(v1), {'entity': '', 'compound': 'eaten', 'word': 'eaten', 'tag': 'v'}(v3), {'entity': '', 'compound': 'me', 'word': 'me', 'tag': 'PRP'}(v5), {'type': 'PATIENT'}(v3,v1), {'type': 'AGENT'}(v3,v5)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        return is_match

    def creation_from_drt(self):
        self.__print_test_title("A drs is created from its written representation")
        drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        expected_drs = Drs.create_from_predicates_string("{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        return is_match

    def creation_from_drt_with_preposition(self):
        self.__print_test_title('A drs is created from its written representation with preposition')
        drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        return is_match

    def sub_isomorphism(self):
        self.__print_test_title('A subgraph is sub-isomorphic to the larger graph')
        large_drs = Drs.create_from_natural_language('The ideas#1 of Jim#2 are silly')
        small_drs = Drs.create_from_natural_language('ideas#3 of Jim#4')
        lst = large_drs.visit(DrsMatcher(small_drs, metric))
        is_match = len(lst) > 0
        return is_match

    def single_clause_test(self):
        self.__print_test_title('A single clause is applied correcly')
        data_drs = Drs.create_from_natural_language('Jim works at Microsoft')
        rule = """
        MATCH "{PERSON}#1 works at {ORG}#2"
        CREATE {}(1), {"type": "WORKS_AT"}(1,2), {}(2)
        """
        knowledge = Knowledge(metric)
        knowledge.add_rules(rule)
        inference = ForwardInference(data_drs, knowledge)
        end_drs, _ = inference.compute()
        expected_drs = Drs.create_from_predicates_string('{}(1), {"type": "WORKS_AT"}(1,2), {}(2)')
        lst = end_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        return is_match

    def test_relation_rules(self):
        self.__print_test_title('The relation rules are applied correctly')

        data_drs = Drs.create_from_natural_language('Jim works at Microsoft')
        knowledge = Knowledge(metric)
        knowledge.add_rules(open(os.path.join(_path, '../rules/recruitment_relations.rules')).read())
        inference = ForwardInference(data_drs, knowledge)
        end_drs, _ = inference.compute()
        expected_drs = Drs.create_from_predicates_string('{}(1), {"text": "WORKS_AT"}(1,2), {}(2)')
        lst = end_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        return is_match

    def test_modal(self):
        self.__print_test_title('The default rules are applied correctly')
        data_drs = Drs.create_from_natural_language('alberto can dance')
        expected_drs = Drs.create_from_predicates_string(
            '{"tag": "MD", "word": "can"}(2), {"type": "MODAL"}(3,2), {"tag": "v"}(3)')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        return is_match

    def test_if_rule(self):
        self.__print_test_title('The conditional is handled correctly')
        data_drs = Drs.create_from_natural_language('If I breathe I am alive')
        expected_drs = Drs.create_from_predicates_string('{}(a), {"type": "CONDITION"}(a,b), {}(b)')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        return is_match

    def test_entity_parsing(self):
        self.__print_test_title('The entities are matched correctly')
        data_drs = Drs.create_from_natural_language('{PERSON} is in {GPE}')
        expected_drs = Drs.create_from_natural_language('John is in London')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        return is_match


if __name__ == "__main__":
    tests = Tests()
    for test_name in dir(Tests):
        if test_name.find("__") != -1:
            continue
        test = getattr(Tests, test_name)
        result_is_true = test(tests)
        if result_is_true:
            print(bcolors.OKGREEN + "True" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "False" + bcolors.ENDC)
