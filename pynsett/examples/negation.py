import os

from pynsett.discourse import Discourse
from pynsett.drt import Drs
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge

_path = os.path.dirname(__file__)

text = "John Smith is not blond"
drs = Drs.create_from_natural_language(text)
drs.plot()
print(drs)