def tag_is_cardinal(tag):
    return tag == "CD"


def tag_is_determiner(tag):
    return tag == "DT" or tag == "WDT"


def tag_is_adjective(tag):
    return tag == "j" or tag == "J" or tag == "JJ" or tag == "JJS" or tag == "JJR" or tag == "PRP$"


def tag_is_noun(tag):
    return tag == "k" or tag == "viz" or tag == "rb" or tag == "n" or tag == "N" or tag == "j" or tag == "J" \
           or tag == "NN" or tag == "NNS" or tag == "NNP" or tag == "NNPS" or tag == "JJ" or tag == "JJS" \
           or tag == "PRP" or tag == "WP" or tag == "PRP"


def tag_is_only_noun(tag):
    return tag == "n" or tag == "N" or tag == "NN" or tag == "NNS" or tag == "NNP" or tag == "NNPS"


def tag_is_verb(tag):
    return tag == "v" or tag == "V" or tag == "VB" or tag == "VBP" or tag == "VBZ" or tag == "VBD" or tag == "VBN" or tag == "VBG"


def tag_is_modal(tag):
    return tag == "MD"


def tag_is_negation(tag, word):
    return (tag == 'AFX' or tag == 'RB') and (word == 'non' or word == 'not')
