import os
import unittest

from pynsett.discourse import Discourse
from pynsett.drt import Drs
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.metric import MetricFactory
from pynsett.drt.drs_matcher import DrsMatcher
from pynsett.writer import RelationTripletsWriter
from pynsett.writer.drt_triplets_writer import DRTTripletsWriter

_path = os.path.dirname(__file__)

metric = MetricFactory.get_best_available_metric()

_knowledge = Knowledge()
_knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())


class PynsettUnitTests(unittest.TestCase):
    def test_copula(self):
        drs = Drs.create_from_natural_language('this is a test')
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_negation(self):
        drs = Drs.create_from_natural_language('John Smith is not blond')
        expected_drs = Drs.create_from_natural_language('John Smith is blond')
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) == 0
        self.assertTrue(is_match)

    def test_negation_matches(self):
        drs = Drs.create_from_natural_language('John Smith is not blond')
        expected_drs = Drs.create_from_natural_language('John Smith is not blond')
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_not_match = len(lst) > 0
        self.assertTrue(is_not_match)

    def test_passive(self):
        drs = Drs.create_from_natural_language('the rabbit is eaten by me')
        expected_drs = Drs.create_from_predicates_string(
            "{'entity': '', 'compound': 'rabbit', 'word': 'rabbit', 'tag': 'n'}(v1), {'entity': '', 'compound': 'eaten', 'word': 'eaten', 'tag': 'v'}(v3), {'entity': '', 'compound': 'me', 'word': 'me', 'tag': 'PRP'}(v5), {'type': 'PATIENT'}(v3,v1), {'type': 'AGENT'}(v3,v5)")
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_creation_from_drt(self):
        drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'is', 'compound': 'is', 'tag': 'v', 'entity': ''}(v1), {'word': 'this', 'compound': 'this', 'tag': 'DT', 'entity': ''}(v0), {'word': 'test', 'compound': 'test', 'tag': 'n', 'entity': ''}(v3), {'type': 'AGENT'}(v1,v0), {'type': 'ATTR'}(v1,v3)")
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_creation_from_drt_with_preposition(self):
        drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        expected_drs = Drs.create_from_predicates_string(
            "{'word': 'ideas', 'entity': '', 'tag': 'n', 'compound': 'ideas'}(v0), {'word': 'Jim', 'entity': '', 'tag': 'n', 'compound': 'Jim'}(v2), {'type': 'of'}(v0,v2)")
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_sub_isomorphism(self):
        large_drs = Drs.create_from_natural_language('The ideas#1 of Jim#2 are silly')
        small_drs = Drs.create_from_natural_language('ideas#3 of Jim#4')
        lst = large_drs.apply(DrsMatcher(small_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_single_clause(self):
        data_drs = Drs.create_from_natural_language('Jim works at Microsoft')
        rule = """
        MATCH "{PERSON}#1 works at {ORG}#2"
        CREATE {}(1), {"type": "WORKS_AT"}(1,2), {}(2)
        """
        knowledge = Knowledge(metric)
        knowledge.add_rules(rule)
        inference = ForwardInference(data_drs, knowledge)
        end_drs = inference.compute()
        expected_drs = Drs.create_from_predicates_string('{}(1), {"type": "WORKS_AT"}(1,2), {}(2)')
        is_match = False
        for drs in end_drs:
            lst = drs[0].apply(DrsMatcher(expected_drs, metric))
            if len(lst) > 0:
                is_match = True
                break
        self.assertTrue(is_match)

    def test_relation_rules(self):
        data_drs = Drs.create_from_natural_language('Jim works at Microsoft')
        knowledge = Knowledge(metric)
        knowledge.add_rules(open(os.path.join(_path, '../rules/generic_relations.rules')).read())
        inference = ForwardInference(data_drs, knowledge)
        end_drs = inference.compute()
        expected_drs = Drs.create_from_predicates_string('{}(1), {"text": "WORKS_AT"}(1,2), {}(2)')
        is_match = False
        for drs in end_drs:
            lst = drs[0].apply(DrsMatcher(expected_drs, metric))
            if len(lst) > 0:
                is_match = True
                break
        self.assertTrue(is_match)

    def test_modal(self):
        data_drs = Drs.create_from_natural_language('alberto can dance')
        expected_drs = Drs.create_from_predicates_string(
            '{"tag": "MD", "word": "can"}(2), {"type": "MODAL"}(3,2), {"tag": "v"}(3)')
        lst = data_drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_if_rule(self):
        data_drs = Drs.create_from_natural_language('If I breathe I am alive')
        expected_drs = Drs.create_from_predicates_string('{}(a), {"type": "CONDITION"}(a,b), {}(b)')
        lst = data_drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 0
        self.assertTrue(is_match)

    def test_entity_parsing(self):
        data_drs = Drs.create_from_natural_language('{PERSON} is in {GPE}')
        expected_drs = Drs.create_from_natural_language('John is in London')
        lst = data_drs.apply(DrsMatcher(expected_drs, metric))
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
        lst = drs_and_weight[0][0].apply(writer)
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
        lst = drs_and_weight[0][0].apply(writer)
        expected_list = [('me', 'OWN', 'dog')]
        self.assertEqual(lst, expected_list)

    def test_personal_pronouns(self):
        sentence = 'I have a red dog'
        drs = Drs.create_from_natural_language(sentence)
        fi = ForwardInference(drs, _knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0][0].apply(writer)
        expected_list = [('I', 'OWN', 'dog')]
        self.assertEqual(lst, expected_list)

    def test_pronoun_coreference(self):
        sentence = 'John drove home where he has a cat.'
        discourse = Discourse(sentence)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('John_0', 'OWN', 'cat')]
        self.assertEqual(triplets, expected_triplets)

    def test_birth_date(self):
        sentence = 'John was born in 1582 or 1583 in Antwerp'
        drs = Drs.create_from_natural_language(sentence)
        fi = ForwardInference(drs, _knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0][0].apply(writer)
        expected_list = [('John', 'BIRTH_DAY', '1582')]
        self.assertEqual(lst, expected_list)

    def test_birth_date2(self):
        sentence = 'John was born in 10 August 1582'
        drs = Drs.create_from_natural_language(sentence)
        fi = ForwardInference(drs, _knowledge)
        drs_and_weight = fi.compute()
        writer = RelationTripletsWriter()
        lst = drs_and_weight[0][0].apply(writer)
        expected_list = [('John', 'BIRTH_DAY', '10_August_1582')]
        self.assertEqual(lst, expected_list)


    def test_multi_sentence_anaphora_masculine_names(self):
        text = "John is happy. He is a carpenter"
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('John_0', 'HAS_ROLE', 'carpenter')]
        self.assertEqual(triplets, expected_triplets)

    def test_multi_sentence_anaphora_feminine_names(self):
        text = "Jane is happy. She is a carpenter"
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('Jane_0', 'HAS_ROLE', 'carpenter')]
        self.assertEqual(triplets, expected_triplets)

    def test_compound_nouns_gender_guess(self):
        text = "Jane Smith is an engineer"
        drs = Drs.create_from_natural_language(text)
        expected_drs = Drs.create_from_predicates_string(
            "{'compound': 'Jane Smith', 'gender_guess': 'f'}(a)")
        lst = drs.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_multiple_people_same_rule(self):
        text = "John is ginger. He is a carpenter. test. Jane is blond. She is a carpenter. "
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('John_0', 'HAS_ROLE', 'carpenter'),
                             ('Jane_1', 'HAS_ROLE', 'carpenter')]
        self.assertTrue(triplets, expected_triplets)

    def test_coreference_is_joined_in_graph(self):
        text = "John is ginger. He is a carpenter. test. Jane is blond. She is a carpenter. "
        discourse = Discourse(text)
        expected_drs = Drs.create_from_predicates_string(
            "{}(a), {}(b), {'type': 'REFERS_TO'}(a,b)")
        lst = discourse._discourse.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_multiple_matcing(self):
        text = "John Smith is blond. He is a carpenter. There is no reason to panic. Sarah Doe is ginger. She is a carpenter."
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('John_Smith_0', 'HAS_BLOND_ROLE', 'carpenter'),
                             ('Sarah_Doe_1', 'HAS_GINGER_ROLE', 'carpenter'),
                             ('John_0', 'HAS_ROLE', 'carpenter'),
                             ('Jane_1', 'HAS_ROLE', 'carpenter')]
        self.assertTrue(triplets, expected_triplets)

    def test_asimov_wiki(self):
        text = open(os.path.join(_path, '../data/wiki_asimov.txt')).read()
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('Isaac_Asimov_0|Asimov_0', 'JOB_TITLE', 'writer'),
                             ('Isaac_Asimov_0|Asimov_0', 'OWNS', 'works'),
                             ('Isaac_Asimov_0|Asimov_0', 'OWNS', 'books')]
        self.assertTrue(triplets, expected_triplets)

        expected_drs = Drs.create_from_predicates_string(
            "{}(a), {'word': 'Boston_University'}(b), {'type': 'at'}(a,b)")
        lst = discourse._discourse.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_two_paragraphs(self):
        text = open(os.path.join(_path, '../data/wiki_asimov_two_paragraphs.txt')).read()
        discourse = Discourse(text)
        extractor = Extractor(discourse, _knowledge)
        triplets = extractor.extract()
        expected_triplets = [('Isaac_Asimov_0|Asimov_0', 'JOB_TITLE', 'writer'),
                             ('he', 'OWNS', 'lifetime'),
                             ('he', 'OWNS', 'stories'),
                             ('Isaac_Asimov_0|Asimov_0', 'OWNS', 'books'),
                             ('he', 'OWNS', 'series'),
                             ('Isaac_Asimov_0|Asimov_0', 'OWNS', 'works')]
        self.assertTrue(triplets, expected_triplets)

        expected_drs = Drs.create_from_predicates_string(
            "{}(a), {'word': 'Boston_University'}(b), {'type': 'at'}(a,b)")
        lst = discourse._discourse.apply(DrsMatcher(expected_drs, metric))
        is_match = len(lst) > 1
        self.assertTrue(is_match)

    def test_drt_graph(self):
        sentence = 'John is tall'
        drs = Drs.create_from_natural_language(sentence)
        writer = DRTTripletsWriter()
        triplets = drs.apply(writer)
        expected_triplets = {'edges': [{'arrows': 'to', 'from': 'v1', 'label': 'AGENT', 'to': 'v0'},
                                       {'arrows': 'to', 'from': 'v1', 'label': 'ADJECTIVE', 'to': 'v2'}],
                             'nodes': [{'id': 'v1', 'label': 'is'},
                                       {'id': 'v0', 'label': 'John'},
                                       {'id': 'v2', 'label': 'tall'}]}
        self.assertEqual(triplets, expected_triplets)


if __name__ == '__main__':
    unittest.main()
