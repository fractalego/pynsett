import os

from nlulite.drt import Drs
from nlulite.knowledge import Knowledge
from nlulite.inference import ForwardInference
from nlulite.writer import RelationTripletsWriter
from nlulite.metric import Metric


_path = os.path.dirname(__file__)

sentence = '{PERSON}#l1 works for {ORG}'
drs = Drs.create_from_natural_language(sentence)
print(drs)
knowledge = Knowledge(Metric())
knowledge.add_rules(open(os.path.join(_path, '../../rules/recruitment_relations.rules')).read())

fi = ForwardInference(drs, knowledge)
drs_and_weight = fi.compute()

writer = RelationTripletsWriter()
print(drs_and_weight[0].visit(writer))
