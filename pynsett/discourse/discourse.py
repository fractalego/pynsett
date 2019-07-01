import logging

from nltk.tokenize import sent_tokenize

from pynsett.auxiliary.names_modifier import SentenceNamesModifier, assign_proper_index_to_nodes_names, \
    DiscourseNamesModifier
from pynsett.discourse.anaphora import AllenCoreferenceVisitorsFactory
from pynsett.discourse.global_graph_visitors import GraphJoinerVisitor, CoreferenceJoinerVisitor
from pynsett.discourse.paragraphs import SimpleParagraphTokenizer
from pynsett.discourse.single_tokens_visitors import HeadTokenVisitor
from ..drt import Drs

_logger = logging.getLogger(__name__)


class DiscourseBase:
    _sentences_list = []
    _drs_list = []
    _discourse = Drs.create_empty()

    @property
    def drs_list(self):
        return self._drs_list

    @property
    def connected_components(self):
        from igraph import WEAK
        g_list = self._discourse._g.clusters(mode=WEAK).subgraphs()
        return [Drs(g) for g in g_list]

    def __getitem__(self, item):
        return self._sentences_list[item], self._drs_list[item]

    def __len__(self):
        return len(self._sentences_list)

    def get_discourse_drs(self):
        return self._discourse

    def apply(self, function):
        return self._discourse.apply(function)


class Paragraph(DiscourseBase):
    def __init__(self, text):
        self._discourse = Drs.create_empty()
        self._drs_list = []

        self._sentences_list = sent_tokenize(text)
        word_nodes = []
        for sentence_index, sentence in enumerate(self._sentences_list):
            try:
                if sentence == '.':
                    continue
                drs = Drs.create_from_natural_language(sentence)
                word_nodes += assign_proper_index_to_nodes_names(drs.word_nodes, sentence_index)
                drs.apply(HeadTokenVisitor(sentence_index))
                drs.apply(SentenceNamesModifier(sentence_index))
                self._drs_list.append(drs)
            except Exception as e:
                _logger.warning('Exception caught in Discourse: ' + str(e))

        coreference_visitor_factory = AllenCoreferenceVisitorsFactory(word_nodes)
        for i, drs in enumerate(self._drs_list):
            drs.apply(coreference_visitor_factory.create())

        self.__create_discourse_graph()

    def __create_discourse_graph(self):
        if len(self._drs_list) == 1:
            self._discourse = self._drs_list[0]
            return
        for drs in self._drs_list:
            self._discourse.apply(GraphJoinerVisitor(drs))
        self._discourse.apply(CoreferenceJoinerVisitor())


class Discourse(DiscourseBase):
    def __init__(self, text):
        paragraphs = self.__divide_into_paragraphs(self.__sanitize_text(text))
        if len(paragraphs) > 1:
            [paragraph._discourse.apply(DiscourseNamesModifier(i)) for i, paragraph in enumerate(paragraphs)]
        self._sentences_list = self.__aggregate_sentence_list_from_paragrahs(paragraphs)
        self._drs_list = self.__aggregate_drs_list_from_paragrahs(paragraphs)
        self._discourse = self.__aggregate_discourse_from_paragrahs(paragraphs)

    def __aggregate_discourse_from_paragrahs(self, paragraphs):
        return Drs.create_union_from_list_of_drs([paragraph.get_discourse_drs() for paragraph in paragraphs])

    def __aggregate_sentence_list_from_paragrahs(self, paragraphs):
        sentence_list = []
        for paragraph in paragraphs:
            sentence_list += paragraph._sentences_list
        return sentence_list

    def __aggregate_drs_list_from_paragrahs(self, paragraphs):
        drs_list = []
        for paragraph in paragraphs:
            drs_list += paragraph.drs_list
        return drs_list

    def __divide_into_paragraphs(self, text):
        paragraphs_texts = SimpleParagraphTokenizer().get_paragraphs(text)
        paragraphs = []
        for text in paragraphs_texts:
            paragraphs.append(Paragraph(text))
        return paragraphs

    def __sanitize_text(self, text):
        text = text.replace('\n', '.\n')
        text = text.replace('.[', '. [')
        text = text.replace('...', '.')
        text = text.replace('..', '.')
        text = text.replace('\n.', '\n')
        return text
