"""Views for app."""

import re
import json
import os
import urllib.parse

from flask import (Blueprint, current_app, redirect, render_template, request,
                   Response, url_for)
from werkzeug.routing import BaseConverter

from ..api import entity_to_name, entity_to_smiles, search, wb_get_entities
from ..rss import (wb_get_author_latest_works, wb_get_venue_latest_works,
                   wb_get_topic_latest_works, wb_get_organization_latest_works,
                   wb_get_sponsor_latest_works)
from ..arxiv import metadata_to_quickstatements, string_to_arxiv
from ..arxiv import get_metadata as get_arxiv_metadata
from ..query import (arxiv_to_qs, cas_to_qs, atomic_symbol_to_qs, doi_to_qs,
                     github_to_qs, biorxiv_to_qs, chemrxiv_to_qs,
                     inchikey_to_qs, issn_to_qs, orcid_to_qs, viaf_to_qs,
                     q_to_class, q_to_dois, random_author, twitter_to_qs,
                     cordis_to_qs, mesh_to_qs, pubmed_to_qs,
                     lipidmaps_to_qs, ror_to_qs, wikipathways_to_qs,
                     pubchem_to_qs, atomic_number_to_qs, ncbi_taxon_to_qs,
                     ncbi_gene_to_qs)
from ..utils import sanitize_q
from ..wikipedia import q_to_bibliography_templates


class RegexConverter(BaseConverter):
    """Converter for regular expression routes.

    References
    ----------
    https://stackoverflow.com/questions/5870188

    """

    def __init__(self, url_map, *items):
        """Set up regular expression matcher."""
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def add_app_url_map_converter(self, func, name=None):
    """Register a custom URL map converters, available application wide.

    References
    ----------
    https://coderwall.com/p/gnafxa/adding-custom-url-map-converters-to-flask-blueprint-objects

    """

    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func

    self.record_once(register_converter)


Blueprint.add_app_url_map_converter = add_app_url_map_converter
main = Blueprint('app', __name__)
main.add_app_url_map_converter(RegexConverter, 'regex')

# Wikidata item identifier matcher
l_pattern = r'<regex(r"L[1-9]\d*"):lexeme>'
L_PATTERN = re.compile(r'L[1-9]\d*')

q_pattern = r'<regex(r"Q[1-9]\d*"):q>'
q1_pattern = r'<regex(r"Q[1-9]\d*"):q1>'
q2_pattern = r'<regex(r"Q[1-9]\d*"):q2>'
Q_PATTERN = re.compile(r'Q[1-9]\d*')

p_pattern = r'<regex(r"P[1-9]\d*"):p>'
P_PATTERN = re.compile(r'P[1-9]\d*')

# https://github.com/d3/d3-3.x-api-reference/blob/master/Ordinal-Scales.md#category20c
d3_category20c = [
    '3182bd', '6baed6', '9ecae1', 'c6dbef',
    'e6550d', 'fd8d3c', 'fdae6b', 'fdd0a2',
    '31a354', '74c476', 'a1d99b', 'c7e9c0',
    '756bb1', '9e9ac8', 'bcbddc', 'dadaeb',
    '636363', '969696', 'bdbdbd', 'd9d9d9'
]

# Wikidata item identifiers matcher
qs_pattern = r'<regex(r"Q[1-9]\d*(?:[^0-9]+Q[1-9]\d*)*"):qs>'


@main.route("/")
def index():
    q = "Q106489997"

    first_initial, last_name = '', ''
    return render_template('cluster.html',
                           q=q,
                           first_initial=first_initial,
                           last_name=last_name,
                           cluster_keywords=json.dumps(
                               __get_keywords_bubble_chart_data())
                           )

@main.route('/author/' + q_pattern)
def show_author(q):
    """Return HTML rendering for specific author.
    Parameters
    ----------
    q : str
        Wikidata item identifier.
    Returns
    -------
    html : str
        Rendered HTML.
    """
    entities = wb_get_entities([q])
    name = entity_to_name(entities[q])
    if name:
        first_initial, last_name = name[0], name.split()[-1]
    else:
        first_initial, last_name = '', ''
    return render_template('author.html', q=q, first_initial=first_initial,
                           last_name=last_name)

@main.route('/author/')
def show_author_empty():
    """Return author index page.
    Returns
    -------
    html : str
        Rendered index page for author view.
    """
    return render_template('author_empty.html')                           


@main.route('/keyword')
def show_keyword():
    query_keyword = request.args.get('kw')
    n_keywords = int(request.args.get('n'))

    first_initial, last_name = '', ''
    return render_template('keyword.html',
                           q=query_keyword,
                           first_initial=first_initial,
                           last_name=last_name,
                           cluster_keywords=json.dumps(__get_keywords_to_authors_chart_data(
                               query_keyword, 1, n_keywords))
                           )


@main.route('/keyword/author')
def show_keyword_of_author():
    author = request.args.get('name')

    first_initial, last_name = '', ''
    return render_template('keyword_author.html',
                           q=author,
                           first_initial=first_initial,
                           last_name=last_name,
                           cluster_keywords=json.dumps(
                               __get_author_to_keywords_chart_data(author))
                           )


# @main.route('/author/')
# def show_author_empty():
#     """Return author index page.
#     Returns
#     -------
#     html : str
#         Rendered index page for author view.
#     """
#     return render_template('author_empty.html')                           


@main.route("/" + l_pattern)
def redirect_l(lexeme):
    """Redirect to Scholia lexeme aspect.

    Parameters
    ----------
    lexeme : str
        Wikidata lexeme identifier

    """
    return redirect(url_for('app.show_lexeme', lexeme=lexeme), code=302)


@main.route("/" + q_pattern)
def redirect_q(q):
    """Detect and redirect to Scholia class page.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    class_ = q_to_class(q)
    method = 'app.show_' + class_
    return redirect(url_for(method, q=q), code=302)


@main.route("/" + p_pattern)
def show_p(p):
    """Detect and redirect to Scholia class page.

    Parameters
    ----------
    p : str
        Wikidata property identifier

    """
    return render_template('property.html', p=p)


@main.route('/biorxiv/<biorxiv_id>')
def show_biorxiv(biorxiv_id):
    """Return HTML rendering for bioRxiv.

    Parameters
    ----------
    biorxiv_id : str
        bioRxiv identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    qs = biorxiv_to_qs(biorxiv_id)
    return _render_work_qs(qs)


@main.route('/chemrxiv/<chemrxiv_id>')
def show_chemrxiv(chemrxiv_id):
    """Return HTML rendering for ChemRxiv.

    Parameters
    ----------
    chemrxiv_id : str
        ChemRxiv identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    qs = chemrxiv_to_qs(chemrxiv_id)
    return _render_work_qs(qs)


@main.route('/arxiv/<arxiv>')
def show_arxiv(arxiv):
    """Return HTML rendering for arxiv.

    Parameters
    ----------
    arxiv : str
        Arxiv identifier.

    Returns
    -------
    html : str
        Rendered HTML.

    See Also
    --------
    show_arxiv_to_quickstatements.

    """
    qs = arxiv_to_qs(arxiv)
    return _render_work_qs(qs)


def _render_work_qs(qs):
    if len(qs) > 0:
        q = qs[0]
        return redirect(url_for('app.show_work', q=q), code=302)
    return render_template('404.html')


@main.route('/arxiv-to-quickstatements')
def show_arxiv_to_quickstatements():
    """Return HTML rendering for arxiv.

    Will look after the 'arxiv' parameter.

    Returns
    -------
    html : str
        Rendered HTML.

    See Also
    --------
    show_arxiv.

    """
    query = request.args.get('arxiv')

    if not query:
        return render_template('arxiv_to_quickstatements.html')

    current_app.logger.debug("query: {}".format(query))

    arxiv = string_to_arxiv(query)
    if not arxiv:
        # Could not identify an arxiv identifier
        return render_template('arxiv_to_quickstatements.html')

    qs = arxiv_to_qs(arxiv)
    if len(qs) > 0:
        # The arxiv is already in Wikidata
        q = qs[0]
        return render_template('arxiv_to_quickstatements.html',
                               arxiv=arxiv, q=q)

    try:
        metadata = get_arxiv_metadata(arxiv)
    except Exception:
        return render_template('arxiv_to_quickstatements.html',
                               arxiv=arxiv)

    quickstatements = metadata_to_quickstatements(metadata)

    # For Quickstatements Version 2 in URL components,
    # TAB and newline should be replace by | and ||
    # https://www.wikidata.org/wiki/Help:QuickStatements
    # Furthermore the '/' also needs to be encoded, but Jinja2 urlencode does
    # not encode that character.
    # https://github.com/pallets/jinja/issues/515
    # Here, we let jinja2 handle the encoding rather than adding an extra
    # parameter
    return render_template('arxiv_to_quickstatements.html',
                           arxiv=arxiv, quickstatements=quickstatements)


@main.route('/faq')
def show_faq():
    """Return rendered FAQ page.

    Returns
    -------
    html : str
        Rendered HTML page for FAQ page.

    """
    return render_template('faq.html')


@main.route('/search')
def show_search():
    """Return search page.

    Returns
    -------
    html : str
        Rendered index page for search view.

    """
    query = request.args.get('q', '')
    if query:
        search_results = search(query)
    else:
        search_results = []
    return render_template('search.html',
                           query=query, search_results=search_results)


@main.route('/about')
def show_about():
    """Return rendered about page.

    Returns
    -------
    html : str
        Rendered HTML page for about page.

    """
    return render_template('about.html')


@main.route('/favicon.ico')
def show_favicon():
    """Detect and redirect for the favicon.ico."""
    return redirect(url_for('static', filename='favicon/favicon.ico'))


def __get_keywords_bubble_chart_data():
    keywords_input_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'keywords_final.json'
    )
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

            # recursive calls to all the authors that have a nearby keyword
            if _name in authors:
                other_keywords = sorted(authors[_name], key=lambda k: k['score'], reverse=True)[:max_n]
                for related_keyword in other_keywords:

                    if related_keyword['topicLabel'] == query_keyword:
                        continue  # skips ciclic link

                    related_encoded = urllib.parse.quote_plus(related_keyword['topicLabel'])
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


def __get_keywords_to_authors_chart_data(query_keyword, max_hops, n_keywords):
    keywords_input_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'keywords_final.json'
    )
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


def __get_author_to_keywords_chart_data(query_author):
    keywords_input_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'keywords_final.json'
    )
    rgb_map = {}
    result = []
    _encoded_name = urllib.parse.quote_plus(query_author)
    with open(keywords_input_file, 'r') as _if:
        data = json.load(_if)
        keywords = data['keywords']
        authors = data['authors']

        rgb_idx = 0
        for related_keyword in authors[query_author]:
            if related_keyword['topicLabel'] not in rgb_map:
                rgb_map[related_keyword['topicLabel']
                ] = d3_category20c[rgb_idx]
                rgb_idx += 1
                if rgb_idx == len(d3_category20c):
                    rgb_idx = 0

            related_encoded = urllib.parse.quote_plus(related_keyword['topicLabel'])
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
