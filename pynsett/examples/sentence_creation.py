import os

from pynsett.discourse.anaphora import SingleSentenceAnaphoraVisitor
from pynsett.discourse.single_tokens_visitors import HeadTokenVisitor
from pynsett.drt import Drs
from pynsett.knowledge import Knowledge
from pynsett.inference import ForwardInference
from pynsett.writer import RelationTripletsWriter


_path = os.path.dirname(__file__)

#sentence = "John has a house"
#sentence = "Centuries later John wrote to his brother Theo"
#sentence = "Hans was born in 1582 or 1583 in Antwerp, then in the Spanish Netherlands, as the son of cloth merchant Franchois Fransz Hals van Mechelen (c.1542–1610) and his second wife Adriaentje van Geertenryck.[2] Like many, Hals' parents fled during[citation needed] the Fall of Antwerp (1584–1585) from the south to Haarlem in the new Dutch Republic in the north, where he lived for the remainder of his life. Hals studied under Flemish émigré Karel van Mander,[2][3] whose Mannerist influence, however, is barely noticeable in Hals' work."
#sentence = 'It is not known whether Hals ever painted landscapes'
#sentence = 'John drove home where he has a cat.'
#sentence = 'His dog was red'
#sentence = 'My own dog is red'
#sentence = 'Jane has a bicycle'
#sentence = 'Jane Smith is an engineer'
#sentence = 'Jane works as an engineer'
#sentence = 'Jane works for Google'
sentence = "John was born in 1582 or 1583 in Antwerp"

drs = Drs.create_from_natural_language(sentence)
print(drs)

anaphora = SingleSentenceAnaphoraVisitor()
drs.apply(anaphora)

head_token_visitor = HeadTokenVisitor(1)
drs.apply(head_token_visitor)

print('---')
print(drs)

knowledge = Knowledge()
knowledge.add_rules(open(os.path.join(_path, '../rules/test.rules')).read())
#knowledge.add_rules(open(os.path.join(_path, '../rules/generic_relations.rules')).read())

fi = ForwardInference(drs, knowledge)
drs_and_weights = fi.compute()

writer = RelationTripletsWriter()
for drs_and_weight in drs_and_weights:
    print(drs_and_weight[0].apply(writer))
