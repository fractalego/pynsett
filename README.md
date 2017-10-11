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


