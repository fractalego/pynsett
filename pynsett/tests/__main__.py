import os
import unittest

from pynsett.drt import Drs
from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.metric import MetricFactory
from pynsett.drt.drs_matcher import DrsMatcher
from pynsett.writer import RelationTripletsWriter

_path = os.path.dirname(__file__)

metric = MetricFactory.get_best_available_metric()


class Tests(unittest.TestCase):
    def copula_test(self):
        drs = Drs.create_from_natural_language('this is a test')
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def passive_test(self):
        drs = Drs.create_from_natural_language('the rabbit is eaten by me')
        expected_drs = Drs.create_from_predicates_string(
            "{'entity': '', 'compound': 'rabbit', 'word': 'rabbit', 'tag': 'n'}(v1), {'entity': '', 'compound': 'eaten', 'word': 'eaten', 'tag': 'v'}(v3), {'entity': '', 'compound': 'me', 'word': 'me', 'tag': 'PRP'}(v5), {'type': 'PATIENT'}(v3,v1), {'type': 'AGENT'}(v3,v5)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def creation_from_drt(self):
        drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def creation_from_drt_with_preposition(self):
        drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        lst = drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def sub_isomorphism(self):
        large_drs = Drs.create_from_natural_language('The ideas#1 of Jim#2 are silly')
        small_drs = Drs.create_from_natural_language('ideas#3 of Jim#4')
        lst = large_drs.visit(DrsMatcher(small_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def single_clause_test(self):
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
        self.assertTrue(is_match)

    def test_relation_rules(self):
        data_drs = Drs.create_from_natural_language('Jim works at Microsoft')
        knowledge = Knowledge(metric)
        knowledge.add_rules(open(os.path.join(_path, '../rules/generic_relations.rules')).read())
        inference = ForwardInference(data_drs, knowledge)
        end_drs, _ = inference.compute()
        expected_drs = Drs.create_from_predicates_string('{}(1), {"text": "WORKS_AT"}(1,2), {}(2)')
        lst = end_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_modal(self):
        data_drs = Drs.create_from_natural_language('alberto can dance')
        expected_drs = Drs.create_from_predicates_string(
            '{"tag": "MD", "word": "can"}(2), {"type": "MODAL"}(3,2), {"tag": "v"}(3)')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_if_rule(self):
        data_drs = Drs.create_from_natural_language('If I breathe I am alive')
        expected_drs = Drs.create_from_predicates_string('{}(a), {"type": "CONDITION"}(a,b), {}(b)')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_entity_parsing(self):
        data_drs = Drs.create_from_natural_language('{PERSON} is in {GPE}')
        expected_drs = Drs.create_from_natural_language('John is in London')
        lst = data_drs.visit(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_OWN_rule(self):
        sentence = 'Jane\'s dog is red'
        drs = Drs.create_from_natural_language(sentence)
        knowledge = Knowledge()
        knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())
        fi = ForwardInference(drs, knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0].visit(writer)
        expected_list = [('Jane', 'OWN', 'dog')]
        self.assertEqual(lst, expected_list)

    def test_possesive_pronouns(self):
        sentence = 'My dog is red'
        drs = Drs.create_from_natural_language(sentence)
        knowledge = Knowledge()
        knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())
        fi = ForwardInference(drs, knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0].visit(writer)
        expected_list = [('me', 'OWN', 'dog')]
        self.assertEqual(lst, expected_list)

    def test_personal_pronouns(self):
        sentence = 'I have a red dog'
        drs = Drs.create_from_natural_language(sentence)
        knowledge = Knowledge()
        knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())
        fi = ForwardInference(drs, knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0].visit(writer)
        expected_list = [('I', 'OWN', 'dog')]
        self.assertEqual(lst, expected_list)
