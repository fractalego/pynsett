import json
import os

import requests

from flask import Flask, Response
from flask import request
from flask import jsonify
from flask_cors import CORS
from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge
from pynsett.auxiliary.transform import transform_triplets_into_api_edges_and_nodes
from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.writer.drt_triplets_writer import DRTTripletsWriter

app = Flask(__name__)
CORS(app)

knowledge = get_wikidata_knowledge()


@app.route('/api/triplets', methods=['POST'])
def get_triplets():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    discourse = Discourse(text)
    extractor = Extractor(discourse, knowledge)
    triplets = extractor.extract()
    return jsonify(transform_triplets_into_api_edges_and_nodes(triplets))


@app.route('/api/drt', methods=['POST'])
def get_drt():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    discourse = Discourse(text)
    writer = DRTTripletsWriter()
    triplets = discourse.apply(writer)
    return jsonify(triplets)


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):
    try:
        src = os.path.join(root_dir(), filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/static/<path>')
def get_resource(path):
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    if mimetype != "text/html":
        path = 'static/' + path
    complete_path = os.path.join(root_dir(), path)
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)


@app.route('/relations')
def get_relations_page():
    path = 'relations.html'
    complete_path = os.path.join(root_dir(), path)
    content = get_file(complete_path)
    return Response(content, mimetype='text/html')


if __name__ == '__main__':
    port = 4001
    app.run(debug=True, port=port, host='0.0.0.0')
    json.loads(requests.post(f'http://localhost:{port}/drt', json={'text': 'test'}).text)
    print('Server is up and running!')
