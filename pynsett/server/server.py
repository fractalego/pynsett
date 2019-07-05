import json
import os

from flask import Flask, Response
from flask import request
from flask import jsonify
from flask_cors import CORS
from pynsett.auxiliary.prior_knowedge import get_wikidata_knowledge
from pynsett.auxiliary.transform import transform_triplets_into_api_edges_and_nodes
from pynsett.discourse import Discourse
from pynsett.extractor import Extractor
from pynsett.knowledge import Knowledge
from pynsett.writer.drt_triplets_writer import DRTTripletsWriter

pynsett_app = Flask('Pynsett')
CORS(pynsett_app)

wiki_knowledge = get_wikidata_knowledge()
knowledge = Knowledge()


@pynsett_app.route('/api/wikidata', methods=['POST'])
def get_wikidata_triplets():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    discourse = Discourse(text)
    extractor = Extractor(discourse, wiki_knowledge)
    triplets = extractor.extract()
    return jsonify(transform_triplets_into_api_edges_and_nodes(triplets))


@pynsett_app.route('/api/relations', methods=['POST'])
def get_triplets():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    text = data['text']
    discourse = Discourse(text)
    extractor = Extractor(discourse, knowledge)
    triplets = extractor.extract()
    return jsonify(transform_triplets_into_api_edges_and_nodes(triplets))


@pynsett_app.route('/api/set_rules', methods=['POST'])
def set_rules():
    if request.method != 'POST':
        return []
    data = json.loads(request.data)
    global knowledge
    knowledge = Knowledge()
    knowledge.add_rules(data['text'])
    return jsonify({'success': True})


@pynsett_app.route('/api/drt', methods=['POST'])
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


@pynsett_app.route('/', defaults={'path': 'index.html'})
@pynsett_app.route('/static/<path>')
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


@pynsett_app.route('/wikidata')
def get_wikidata_page():
    path = 'wikidata.html'
    complete_path = os.path.join(root_dir(), path)
    content = get_file(complete_path)
    return Response(content, mimetype='text/html')


@pynsett_app.route('/relations')
def get_programmable_relations_page():
    path = 'relations.html'
    complete_path = os.path.join(root_dir(), path)
    content = get_file(complete_path)
    return Response(content, mimetype='text/html')


if __name__ == '__main__':
    port = 4001
    pynsett_app.run(debug=True, port=port, host='0.0.0.0', use_reloader=False)
