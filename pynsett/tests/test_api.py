import json
import requests

from unittest import TestCase


class TestAPI(TestCase):
    def test_simple_triplet(self):
        text = "John is a writer."
        triplets = json.loads(requests.post('http://localhost:4001/api/wikidata', json={'text': text}).text)
        expected_triplets = [['John', 'JOB_TITLE', 'writer']]
        self.assertEqual(expected_triplets, triplets)

    def test_drt(self):
        text = "John is tall."
        triplets = json.loads(requests.post('http://localhost:4001/api/drt', json={'text': text}).text)
        expected_triplets = {'edges': [{'arrows': 'to', 'from': 'v1', 'label': 'AGENT', 'to': 'v0'},
                                       {'arrows': 'to', 'from': 'v1', 'label': 'ADJECTIVE', 'to': 'v2'}],
                             'nodes': [{'id': 'v1', 'label': 'is'},
                                       {'id': 'v0', 'label': 'John'},
                                       {'id': 'v2', 'label': 'tall'}]}

        self.assertEqual(expected_triplets, triplets)
