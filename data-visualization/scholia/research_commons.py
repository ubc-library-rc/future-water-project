"""Views for app."""

import re
import json
import os
import urllib.parse

from flask import (Blueprint, current_app, redirect,
                   render_template, request, Response, url_for)
from werkzeug.routing import BaseConverter


# https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category20c
d3_category20c = [
    '3182bd', '6baed6', '9ecae1', 'c6dbef',
    'e6550d', 'fd8d3c', 'fdae6b', 'fdd0a2',
    '31a354', '74c476', 'a1d99b', 'c7e9c0',
    '756bb1', '9e9ac8', 'bcbddc', 'dadaeb',
    '636363', '969696', 'bdbdbd', 'd9d9d9'
]

keywords_input_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'resources',
    'keywords_final.json'
)


def get_keywords_bubble_chart_data():

    keywords = []
    with open(keywords_input_file, 'r') as _if:
        data = json.load(_if)
        for kw, authors in data['keywords'].items():
            # https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python
            encoded = urllib.parse.quote_plus(kw)
            _new_entry = {
                "topic": {
                    "type": "uri",
                    "value": f"http://localhost:8100/keyword?kw={encoded}&n=2"
                },
                "score": {
                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                    "type": "literal",
                    "value": str(len(authors))
                },
                "topicLabel": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": kw
                }
            }
            keywords.append(_new_entry)
    result = {
        "head": {
            "vars": [
                "score",
                "topic",
                "topicLabel"
            ]
        },
        "results": {
            "bindings": keywords
        }
    }
    return result


def __find_keywords_cluster_members(query_keyword, current_hop, max_hops, already_visited, result, keywords, authors,
                                    max_n=3):
    if query_keyword not in keywords:
        return
    if query_keyword in already_visited:
        return

    rgb_idx = 0
    rgb_map = {}
    if query_keyword not in already_visited and current_hop <= max_hops:

        if query_keyword not in rgb_map:
            rgb_map[query_keyword] = d3_category20c[rgb_idx]
            rgb_idx += 1
            if rgb_idx == len(d3_category20c):
                rgb_idx = 0

        already_visited.append(query_keyword)
        authors_in_keyword = keywords[query_keyword]
        encoded = urllib.parse.quote_plus(query_keyword)

        all_authors = [author['topicLabel'] for author in authors_in_keyword]
        for author in authors_in_keyword:
            _name = author['topicLabel']
            _encoded_name = urllib.parse.quote_plus(_name)
            _new_entry = {
                "author1": {
                    "type": "uri",
                    "value": f"http://localhost:8100/keyword?kw={encoded}&n={max_n}"
                },
                "author2": {
                    "type": "uri",
                    "value": f"http://localhost:8100/keyword/author?name={_encoded_name}"
                },
                "author1Label": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": query_keyword
                },
                "author2Label": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": _name
                },
                "rgb": {
                    "type": "literal",
                    "value": rgb_map[query_keyword]
                }
            }
            result.append(_new_entry)

            if _name in authors:
                other_keywords = sorted(
                    authors[_name], key=lambda k: k['score'], reverse=True)[:max_n]
                for related_keyword in other_keywords:

                    if related_keyword['topicLabel'] == query_keyword:
                        continue  # skips ciclic link

                    related_encoded = urllib.parse.quote_plus(
                        related_keyword['topicLabel'])
                    _new_entry = {
                        "author1": {
                            "type": "uri",
                            "value": f"http://localhost:8100/keyword/author?name={_encoded_name}"
                        },
                        "author2": {
                            "type": "uri",
                            "value": f"http://localhost:8100/keyword?kw={related_encoded}&n={max_n}"
                        },
                        "author1Label": {
                            "xml:lang": "en",
                            "type": "literal",
                            "value": _name
                        },
                        "author2Label": {
                            "xml:lang": "en",
                            "type": "literal",
                            "value": related_keyword['topicLabel']
                        }
                    }
                    result.append(_new_entry)

                    if related_keyword['topicLabel'] not in rgb_map:
                        rgb_map[related_keyword['topicLabel']
                                ] = d3_category20c[rgb_idx]
                        rgb_idx += 1
                        if rgb_idx == len(d3_category20c):
                            rgb_idx = 0

                    _new_entry = {
                        "author1": {
                            "type": "uri",
                            "value": f"http://localhost:8100/keyword?kw={related_encoded}&n={max_n}"
                        },
                        "author1Label": {
                            "xml:lang": "en",
                            "type": "literal",
                            "value": related_keyword['topicLabel']
                        },
                        "rgb": {
                            "type": "literal",
                            "value": rgb_map[related_keyword['topicLabel']]
                        }

                    }
                    result.append(_new_entry)


def get_keywords_to_authors_chart_data(query_keyword, max_hops, n_keywords):
    keywords = []
    with open(keywords_input_file, 'r') as _if:
        data = json.load(_if)
        keywords_authors_list = data['keywords']
        authors_keywords_list = data['authors']

        __find_keywords_cluster_members(
            query_keyword,
            0,
            max_hops,
            [],
            keywords,
            keywords_authors_list,
            authors_keywords_list,
            max_n=n_keywords)

    result = {
        "head": {
            "vars": [
                "author1",
                "author1Label",
                "rgb",
                "author2",
                "author2Label"
            ]
        },
        "results": {
            "bindings": keywords
        }
    }
    return result


def get_author_to_keywords_chart_data(query_author):
    rgb_map = {}
    result = []
    _encoded_name = urllib.parse.quote_plus(query_author)
    with open(keywords_input_file, 'r') as _if:
        data = json.load(_if)
        authors = data['authors']

        rgb_idx = 0
        for related_keyword in authors[query_author]:
            if related_keyword['topicLabel'] not in rgb_map:
                rgb_map[related_keyword['topicLabel']
                        ] = d3_category20c[rgb_idx]
                rgb_idx += 1
                if rgb_idx == len(d3_category20c):
                    rgb_idx = 0

            related_encoded = urllib.parse.quote_plus(
                related_keyword['topicLabel'])
            _new_entry = {
                "author2": {
                    "type": "uri",
                    "value": f"http://localhost:8100/keyword/author?name={_encoded_name}"
                },
                "author1": {
                    "type": "uri",
                    "value": f"http://localhost:8100/keyword?kw={related_encoded}&n=2"
                },
                "author2Label": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": query_author
                },
                "author1Label": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": related_keyword['topicLabel']
                },
                "rgb": {
                    "type": "literal",
                    "value": rgb_map[related_keyword['topicLabel']]
                }
            }

            result.append(_new_entry)

    return {
        "head": {
            "vars": [
                "author1",
                "author1Label",
                "rgb",
                "author2",
                "author2Label"
            ]
        },
        "results": {
            "bindings": result
        }
    }
