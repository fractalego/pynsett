from pynsett.inference import ForwardInference
from pynsett.writer import RelationTripletsWriter


class Extractor:
    def __init__(self, discourse, knowledge):
        '''
        The Extractor class extract the triplets from the a discourse.

        :param discourse: the text to extract information from
        :param knowledge: the knowledge to use upon extracting triplets
        '''
        self._discourse = discourse
        self._knowledge = knowledge

    def extract(self):
        '''
        :return: A list of the extracted triplets
        '''
        triplets = []
        discouse_triplets = self.__map_all_sentences_using_best_match(self._discourse.connected_components)
        if discouse_triplets:
            triplets += discouse_triplets
        return sorted(list(set(triplets)), key=lambda x: x[1])

    # Private
    def __map_all_sentences_using_best_match(self, drs_list):
        triplets = []
        for drs in drs_list:
            triplets += self.__map_sentence_using_best_match(drs)
        return [item for sublist in triplets for item in sublist]

    def __map_sentence_using_best_match(self, data):
        inference = ForwardInference(data, self._knowledge)
        results = inference.compute()
        writer = RelationTripletsWriter()
        triplets = [result[0].apply(writer) for result in results]
        return triplets
