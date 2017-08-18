from nltk.tokenize import sent_tokenize
from ..drt import Drs


class Discourse:
    def __init__(self, text):
        self.drs_list = []
        self.sentences_list = sent_tokenize(text)
        for sentence_index, sentence in enumerate(self.sentences_list):
            sentence = sentence.replace('\n', '')
            self.drs_list.append(Drs.create_from_natural_language(sentence))

    # Iterator operations

    def __getitem__(self, item):
        return self.sentences_list[item], self.drs_list[item]

    def __len__(self):
        return len(self.sentences_list)
