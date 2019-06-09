import os
import spacy

from ..auxiliary import tag_is_verb, tag_is_noun, tag_is_adjective
from ..auxiliary import Collator

parser = spacy.load('en_core_web_lg')

_path = os.path.dirname(__file__)


def create_word_nodes(names, words, tags, types, lemmas, head_tokens, entities):
    return [{'name': name,
             'word': word,
             'tag': tag,
             'type': type,
             'lemma': lemma,
             'entity': entity,
             'head_token': head_token}
            for name, word, tag, type, lemma, entity, head_token
            in zip(names, words, tags, types, lemmas, entities, head_tokens)]


def simplify_tag(tag):
    if tag == 'PRP' or tag == 'PRP$':
        return tag
    if tag_is_adjective(tag):
        return 'j'
    if tag_is_noun(tag):
        return 'n'
    if tag_is_verb(tag):
        return 'v'
    return tag


class SpacyParser:
    _character_that_opens_entity_tag = '{'
    _character_that_closes_entity_tag = '}'
    _character_that_defines_unifier_string = '#'
    _word_substitution = {'(': 'LRB', ')': 'RRB'}
    _set_of_masculine_names = set(
        [item.replace('\n', '') for item in open(os.path.join(_path, '../data/masculine_names.txt')).readlines()])
    _set_of_feminine_names = set(
        [item.replace('\n', '') for item in open(os.path.join(_path, '../data/feminine_names.txt')).readlines()])

    collator = Collator(names_to_collate_forward=[_character_that_opens_entity_tag],
                        names_to_collate_backward=[_character_that_closes_entity_tag])

    def __init__(self, graph_database):
        self.parser = parser
        self.db = graph_database

    def execute(self, sentence):
        words = self.__get_words(sentence)
        words = self.collator.collate(words)
        names, words = self.__get_names(words)
        entities, words = self.__get_entities(words)

        edges, tags, types, lemmas, head_tokens = self.__get_edges_tags_types_and_entities(names, words, entities)
        g = self.__create_graph_from_elements(names, words, edges, tags, types, lemmas, entities, head_tokens)

        return {'graph': g,
                'word_nodes': create_word_nodes(names, words, tags, types, lemmas, head_tokens, entities),
                }

    # Private

    def __get_words(self, sentence):
        words = []
        tokens = self.parser.tokenizer(sentence)
        for _, item in enumerate(tokens):
            word = item.orth_
            if word in self._word_substitution:
                word = self._word_substitution[word]
            if not word:
                word = '.'
            words.append(word)
        return words

    def __get_names(self, words):
        new_words = []
        names = []
        for index, item in enumerate(words):
            splitted_word = item.split(self._character_that_defines_unifier_string)
            word = splitted_word[0].strip()
            new_words.append(word)
            if len(splitted_word) > 1:
                names.append(splitted_word[1])
            else:
                names.append("v" + str(index))
        return names, new_words

    def __get_entities(self, words):
        new_words = []
        entities = []
        for word in words:
            entity = ''
            if not word:
                word = '.'
            if word[0] == self._character_that_opens_entity_tag and word[-1] == self._character_that_closes_entity_tag:
                word = word[1:-1]
                entity = word
            new_words.append(word)
            entities.append(entity)
        return entities, new_words

    def __get_lemma_with_correct_capital_letters(self, lemma, word, tag):
        if tag == 'PRP$' or tag == 'PRP':
            return word.lower()
        if lemma.lower() == word.lower() or word in self._word_substitution:
            return word
        return lemma

    def __get_edges_tags_types_and_entities(self, names, words, entities):
        sentence = ' '.join(words)
        parsed = self.parser(sentence, 'utf8')
        edges = []
        tags = []
        types = []
        lemmas = []
        head_tokens = []
        i = 0
        items_dict = dict()
        for item in parsed:
            items_dict[item.idx] = i
            i += 1
        head_token_index = items_dict[self.__get_head_token_idx(parsed)]
        for item in parsed:
            index = items_dict[item.idx]
            if index == head_token_index:
                head_tokens.append(True)
            else:
                head_tokens.append(False)
            for child_index in [items_dict[l.idx] for l in item.children]:
                edges.append((index, child_index))
            tags.append(simplify_tag(item.tag_))
            types.append(item.dep_)
            lemmas.append(self.__get_lemma_with_correct_capital_letters(item.lemma_, item.orth_, item.tag_))
        for i, entity in enumerate(entities):
            token = parsed[i]
            if not entity:
                entities[i] = token.ent_type_
            if token.tag_ == 'PRP' and token.orth_.lower() != 'it':
                entities[i] = 'PERSON'
                lemmas[i] = token.orth_.lower()
        return edges, tags, types, lemmas, head_tokens

    def __get_gender_guess(self, compound, entity):
        if entity != 'PERSON':
            return None
        names = compound.split()
        for name in names:
            if name in self._set_of_feminine_names:
                return 'f'
            if name in self._set_of_masculine_names:
                return 'm'
        return None

    def __get_head_token_idx(self, tokens):
        for token in tokens:
            if token.dep_ == 'ROOT':
                return token.idx
        return -1

    def __create_graph_from_elements(self, names, words, edges, tags, types, lemmas, entities, head_tokens):
        db = self.db
        for edge in edges:
            lhs_vertex = edge[0]
            rhs_vertex = edge[1]
            lhs_name = names[lhs_vertex]
            rhs_name = names[rhs_vertex]
            lhs_word = words[lhs_vertex]
            rhs_word = words[rhs_vertex]
            lhs_lemma = lemmas[lhs_vertex]
            rhs_lemma = lemmas[rhs_vertex]
            lhs_entity = entities[lhs_vertex]
            rhs_entity = entities[rhs_vertex]
            lhs_compound = lhs_word
            rhs_compound = rhs_word
            lhs_tag = tags[lhs_vertex]
            rhs_tag = tags[rhs_vertex]
            edge_type = types[rhs_vertex].upper()
            lhs_head_token = head_tokens[lhs_vertex]
            rhs_head_token = head_tokens[rhs_vertex]

            if lhs_entity == lhs_word:
                lhs_word = '*'
                lhs_tag = '*'
                lhs_compound = '*'
                lhs_lemma = '*'
            if rhs_entity == rhs_word:
                rhs_word = '*'
                rhs_tag = '*'
                rhs_compound = '*'
                rhs_lemma = '*'

            lhs_dict = {'word': lhs_word,
                        'tag': lhs_tag,
                        'compound': lhs_compound,
                        'entity': lhs_entity,
                        'lemma': lhs_lemma,
                        'gender_guess': self.__get_gender_guess(lhs_compound, lhs_entity),
                        'is_head_token': lhs_head_token,
                        'refers_to': None,
                        'negated': 'false'}
            lhs_string = str(lhs_dict) + '(' + lhs_name + ')'
            rhs_dict = {'word': rhs_word,
                        'tag': rhs_tag,
                        'compound': rhs_compound,
                        'entity': rhs_entity,
                        'lemma': rhs_lemma,
                        'gender_guess': self.__get_gender_guess(rhs_word, rhs_entity),
                        'is_head_token': rhs_head_token,
                        'refers_to': None,
                        'negated': 'false'}
            rhs_string = str(rhs_dict) + '(' + rhs_name + ')'

            edge_dict = {'type': edge_type}
            edge_string = str(edge_dict) + '(' + lhs_name + ',' + rhs_name + ')'
            query_string = 'CREATE ' + lhs_string + ',' + edge_string + ',' + rhs_string
            db.query(query_string)
        return db
