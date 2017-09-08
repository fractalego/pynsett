import os

from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.writer import RelationTripletsWriter
from pynsett.metric import Metric
from pynsett.discourse import Discourse

_path = os.path.dirname(__file__)


def map_sentence_using_best_match(knowledge, large_drs):
    data = large_drs
    inference = ForwardInference(data, knowledge)
    result = inference.compute()
    triplets = []
    writer = RelationTripletsWriter()
    triplets += result[0].visit(writer)
    return triplets


def map_sentence_using_fuzzy_static_models_semantics(knowledge, large_drs):
    data = large_drs
    inference = ForwardInference(data, knowledge)
    result = inference.compute_with_static_models_semantics()
    triplets = []
    writer = RelationTripletsWriter()
    for item in result:
        triplets += item[0].visit(writer)
    return triplets


if __name__ == "__main__":
    import time

    print('Starting the Knowledge.')
    knowledge = Knowledge(Metric())
    print('Knowledge started.')

    knowledge.add_rules(open(os.path.join(_path, '../../rules/recruitment_relations.rules')).read())

    # text = open('data/angel_text.txt').read()
    text = open(os.path.join(_path, '../../data/profile.txt')).read()
    discourse = Discourse(text)
    triplets = []
    start = time.time()
    for _, drs in discourse:
        sentence_triplets = map_sentence_using_best_match(
            knowledge, drs)
        if sentence_triplets:
            triplets += sentence_triplets

    end = time.time()
    print('total_time', (end - start), 'for', len(discourse), 'sentences')
    for triplet in triplets:
        print(triplet)
