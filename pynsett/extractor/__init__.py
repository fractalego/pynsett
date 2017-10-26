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
        for _, drs in self._discourse:
            sentence_triplets = self.__map_sentence_using_best_match(drs)
            if sentence_triplets:
                triplets += sentence_triplets
        return sorted(list(set(triplets)), key=lambda x: x[1])

    # Private

    def __map_sentence_using_best_match(self, large_drs):
        data = large_drs
        inference = ForwardInference(data, self._knowledge)
        results = inference.compute()
        triplets = []
        writer = RelationTripletsWriter()
        for result in results:
            triplets += result[0].visit(writer)
        return triplets
