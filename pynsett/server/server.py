import json

from flask import Flask
from flask import request
from flask import jsonify

from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge
from pynsett.discourse import Discourse
from pynsett.extractor import Extractor

app = Flask(__name__)

knowledge = get_wikidata_knowledge()


@app.route('/triplets', methods=['POST'])
def get_triplets():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    discourse = Discourse(text)
    extractor = Extractor(discourse, knowledge)
    triplets = extractor.extract()
    return jsonify(triplets)


if __name__ == '__main__':
    app.run(debug=True, port=4001, host='0.0.0.0')
