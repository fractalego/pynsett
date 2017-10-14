Pynsett: A lightweight relation extraction tool
===============================================

Installation
------------

The basic version can be installed by typing
```bash
pip3 install pynsett
```

If you want to install the additional models, please type
```bash
python3 -m pynsett download
```

What is Pynsett
---------------

Pynsett is a programmable relation extractor. 
The user sets up a set of rules which are used to parse any English text. 
As a result, Pynsett returns a list of triplets as defined in the rules.


Example usage
-------------

Let's assume we want to extract wikidata relations from a file named 'test.txt'.
An example code would be

```python
import os

from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge


if __name__ == "__main__":
    text = open(os.path.join(_path, 'test.txt')).read()
    discourse = Discourse(text)

    extractor = Extractor(discourse, get_wikidata_knowledge())
    triplets = extractor.extract()

    for triplet in triplets:
        print(triplet)
```

The distribution comes with two sets of rules: The generic knowledge, accessible using
pynsett.auxiliary.prior_knowledge.get_generic_knowledge(), and the wikidata knowledge, which
can be loaded using pynsett.auxiliary.prior_knowledge.get_wikidata_knowledge()


Create new rules for extraction
-------------------------------

Let's assume we are writing a new file called "my_own_rules.rules".
An example of a new set of rules can be the following:

```bash
MATCH "Jane is an engineer"
CREATE {'text': 'Relation found!'}(node_name);
```

This rule matches a specific sentence in a text ("Jane is an engineer") and creates a node;
the node contains the text "Relation found!".

The system is flexible: The verb conjugation does not matter
("Jane will be an engineer" and "Jane was an engineer" match as well), synonyms
are resolved automatically ("Jane is a developer" matches too).

That rule is not very useful. Maybe a more useful one can extract the subject
```bash
MATCH "Jane#node is an engineer"
CREATE {}(node);
```

Here the symbol #1 `gives a name` to Jane. That name can be used when creating the node {}(1).
The node inherits the properties from the word `Jane`. For example node['text'] is "Jane".

A more generic rule uses the entity type (Jane is a PERSON)

```bash
MATCH "{PERSON}#node is an engineer"
CREATE {}(node);
```

This rule matches all the sentences where the subject is a person (compatibly with the internal
NER). The name of the person is associated to the node.

There are 18 entity types that you can type within brackets:
CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL,
ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART


In the end, this is a relation extractor. Relations are created by connecting at least
two elements in a sentence

```bash
MATCH "{PERSON}#1 is an engineer#2"
CREATE {}(1), {'type': 'relation', 'text': 'HAS_ROLE'}(1,2), {}(2);
```

There you go, a person is now connected with a role: Node 1 is whoever matches for node 1 and
the profession is "engineer". The properties of the words are put into node 1 and 2.

This seems a little bit limiting, because the previous relations only works for engineers.
Let us define a `word cloud` and call it "ROLE".

```bash
DEFINE ROLE AS [engineer, architect, physicist, doctor];

MATCH "{PERSON}#1 is a ROLE#2"
CREATE {}(1), {'type': 'relation', 'text': 'HAS_ROLE'}(1,2), {}(2);
```

As a final touch let us make the text a little bit nicer to the eyes: Let's use PERSON instead
of {PERSON}

```bash
DEFINE PERSON AS {PERSON};
DEFINE ROLE AS [engineer, architect, physicist, doctor];

MATCH "PERSON#1 is a ROLE#2"
CREATE {}(1), {'type': 'relation', 'text': 'HAS_ROLE'}(1,2), {}(2);
```


Use the extraction rules
------------------------

If you have a specific file with the extraction rules, you can load it by creating a new
Knowledge object:

```python
from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge
from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge


if __name__ == "__main__":
    text = open(os.path.join(_path, 'test.txt')).read()
    discourse = Discourse(text)

    knowledge = Knowledge()
    knowledge.add_rules(open('./my_own_rules.rules').read())

    extractor = Extractor(discourse, knowledge)
    triplets = extractor.extract()

    for triplet in triplets:
        print(triplet)
```



