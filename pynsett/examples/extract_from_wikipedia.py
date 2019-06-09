import os

from pynsett.discourse import Discourse
from pynsett.extractor import Extractor

_path = os.path.dirname(__file__)

if __name__ == "__main__":
    import time
    from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge

    knowledge = get_wikidata_knowledge()

    text = open(os.path.join(_path, '../data/wiki_asimov_two_paragraphs.txt')).read()

    start = time.time()
    discourse = Discourse(text)
    discourse._discourse.plot()
    extractor = Extractor(discourse, knowledge)
    triplets = extractor.extract()
    end = time.time()

    print('total_time', (end - start), 'for', len(discourse), 'sentences')
    for triplet in triplets:
        print(triplet)
