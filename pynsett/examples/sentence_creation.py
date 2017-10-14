import os

from pynsett.drt import Drs
from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.writer import RelationTripletsWriter


_path = os.path.dirname(__file__)

sentence = 'I have a bicycle'
#sentence = 'My own dog is red'
#sentence = 'Jane has a bicycle'
#sentence = 'Jane is an engineer'
#sentence = 'Jane works as an engineer'
#sentence = 'Jane works for Google'
drs = Drs.create_from_natural_language(sentence)
print(drs)
knowledge = Knowledge()
knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())
#knowledge.add_rules(open(os.path.join(_path, '../rules/generic_relations.rules')).read())

fi = ForwardInference(drs, knowledge)
drs_and_weight = fi.compute()

writer = RelationTripletsWriter()
print(drs_and_weight[0].visit(writer))
