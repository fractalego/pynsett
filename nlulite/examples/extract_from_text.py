import os

from nlulite.drt import Drs
from nlulite.knowledge import Knowledge
from nlulite.inference import ForwardInference
from nlulite.writer import RelationTripletsWriter
from nlulite.metric import Metric


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
    from nltk.tokenize import sent_tokenize

    print('Starting the Knowledge.')
    knowledge = Knowledge(Metric())
    print('Knowledge started.')

    knowledge.add_rules(open(os.path.join(_path, '../../rules/recruitment_relations.rules')).read())

    # text = open('data/angel_text.txt').read()
    text = open(os.path.join(_path, '../../data/profile.txt')).read()
    sentences_list = sent_tokenize(text)
    triplets = []
    start = time.time()
    for sentence_index, sentence in enumerate(sentences_list):
        sentence = sentence.replace('\n', '')
        try:
            drs = Drs.create_from_natural_language(sentence)
            sentence_triplets = map_sentence_using_best_match(
                knowledge, drs)
            if sentence_triplets:
                triplets += sentence_triplets
        except:
            pass
    end = time.time()
    print('total_time', (end - start), 'for', len(sentences_list), 'sentences')
    for triplet in triplets:
        print(triplet)
