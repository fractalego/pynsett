import os

from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge

_path = os.path.dirname(__file__)

text = "This is a test. This is another."

knowledge = Knowledge()
knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())

discourse = Discourse(text)
extractor = Extractor(discourse, knowledge)
triplets = extractor.extract()

for triplet in triplets:
    print(triplet)

#for drs in discourse._drs_list:
#    print(drs)