import os

from pynsett.discourse import Discourse
from pynsett.extractor import Extractor

_path = os.path.dirname(__file__)

if __name__ == "__main__":
    import time
    from pynsett.auxiliary.prior_knowedge import get_generic_knowledge

    text = open(os.path.join(_path, '../data/profile.txt')).read()
    discourse = Discourse(text)

    extractor = Extractor(discourse, get_generic_knowledge())
    start = time.time()
    triplets = extractor.extract()
    end = time.time()

    print('total_time', (end - start), 'for', len(discourse), 'sentences')
    for triplet in triplets:
        print(triplet)
