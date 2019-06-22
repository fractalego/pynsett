import json

import requests
from flask import Flask
from flask import request
from flask import jsonify

from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge
from pynsett.discourse import Discourse
from pynsett.drt import Drs
from pynsett.extractor import Extractor
from pynsett.writer.drt_triplets_writer import DRTTripletsWriter

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


@app.route('/drt', methods=['POST'])
def get_drt():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    drs = Drs.create_from_natural_language(text)
    writer = DRTTripletsWriter()
    triplets = drs.apply(writer)
    return jsonify(triplets)


if __name__ == '__main__':
    port = 4001
    app.run(debug=True, port=port, host='0.0.0.0')
    triplets = json.loads(requests.post(f'http://localhost:{port}/drt', json={'text': 'test'}).text)
