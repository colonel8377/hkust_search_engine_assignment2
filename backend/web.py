#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import coloredlogs
from flask import Flask, jsonify
from flask_cors import CORS

from initialize_search_tries import init_weighted_keywords, init_tries, parse_json
from se_sample import search_api, suggest_api

app = Flask(__name__)
logger = logging.getLogger(__name__)

paper_dict = parse_json('paper.json')
paper_tries, paper_word_count = init_tries(paper_dict=paper_dict, is_only_abstract=False)
paper_word_weight = init_weighted_keywords(paper_tries, paper_word_count)
paper_number = len(paper_dict)


@app.route('/search/query/<query>')
def search(query):
    result = search_api(query)
    re = {"docs": result}
    rst = jsonify(re)
    return rst


@app.route('/search/suggest/<key>')
def suggest(key):
    suggestion_titles = suggest_api(key)
    result = {'suggestions': suggestion_titles}
    re = {'mySuggester': result}
    rst = jsonify(re)
    return rst


def create_app():
    init_log()
    supports_credentials = True
    init_app(app, supports_credentials)
    return app


def init_app(app, supports_credentials):
    CORS(app, supports_credentials=supports_credentials)


def init_log():
    coloredlogs.install(level='info',
                        fmt='%(asctime)s.%(msecs)03d [%(levelname)s] %(process)d %(name)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
