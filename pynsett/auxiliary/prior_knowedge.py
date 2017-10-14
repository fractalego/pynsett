import os

from pynsett.knowledge import Knowledge

_path = os.path.dirname(__file__)


def get_generic_knowledge():
    knowledge = Knowledge()
    knowledge.add_rules(open(os.path.join(_path, '../rules/generic_relations.rules')).read())
    return knowledge


def get_wikidata_knowledge():
    knowledge = Knowledge()
    knowledge.add_rules(open(os.path.join(_path, '../rules/wikidata.rules')).read())
    return knowledge
