import logging
import os

from parvusdb import GraphDatabase

_path = os.path.dirname(__file__)


class Anaphora:
    __logger = logging.getLogger(__name__)
    _db = GraphDatabase(g)

    def __init__(self):
        self._rules = open(os.path.join(_path, '../rules/anaphora.parvus')).read()

    def apply_on_one_drs(self, drs):
        pass