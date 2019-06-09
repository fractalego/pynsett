import json
import requests

from unittest import TestCase


class TestAPI(TestCase):
    def test_simple_triplet(self):
        text = "John is a writer."
        triplets = json.loads(requests.post('http://localhost:4001/triplets', json={'text': text}).text)
        expected_triplets = [['John', 'JOB_TITLE', 'writer']]
        self.assertEqual(expected_triplets, triplets)
