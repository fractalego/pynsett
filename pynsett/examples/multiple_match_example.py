import os

from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge

_path = os.path.dirname(__file__)

text = "John Smith is blond. He is a carpenter. There is no reason to panic. Sarah Doe is ginger. She is a carpenter. "


knowledge = Knowledge()
knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())

discourse = Discourse(text)
discourse._discourse.plot()


extractor = Extractor(discourse, knowledge)
triplets = extractor.extract()

for triplet in triplets:
    print(triplet)
