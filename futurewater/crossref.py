from __future__ import print_function

import json
import logging
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request

import requests
from Levenshtein import ratio

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()


def get_publications(ocrid, dois=None):
    if not dois:
        dois = []
    query = f"https://api.crossref.org/works?filter=has-orcid:true,orcid:{ocrid}&mailto=msarthur@cs.ubc.ca"
    headers = {
        'User-Agent': 'Scholia',
    }
    response_data = requests.get(
        query,
        headers=headers).json()

    # FIXME: needs pagination
    if response_data and 'message' in response_data:
        return [item for item in response_data['message']['items'] if item['DOI'] not in dois]
    return None


def get_publication(title):
    EMPTY_RESULT = {
        "crossref_title": "",
        "similarity": 0,
        "doi": ""
    }

    api_url = "https://api.crossref.org/works?"
    params = {"rows": "5", "query.bibliographic": title}
    url = api_url + urlencode(params, quote_via=quote_plus)

    request = Request(url)
    request.add_header("User-Agent",
                       "OpenAPC DOI Importer (https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py; mailto:openapc@uni-bielefeld.de)")
    full_data = None
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content)
        items = data["message"]["items"]
        most_similar = EMPTY_RESULT
        for item in items:
            if "title" not in item:
                continue
            title = item["title"].pop()
            result = {
                "crossref_title": title,
                "similarity": ratio(title.lower(), params["query.bibliographic"].lower()),
                "doi": item["DOI"]
            }
            if most_similar["similarity"] < result["similarity"]:
                most_similar = result
                full_data = item
        return {"success": True, "result": most_similar, "crossref": full_data}
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}


def get_author(author_name, max_results=100, sim_threshold=.9):
    EMPTY_RESULT = {
        "crossref_title": "",
        "similarity": 0,
        "doi": ""
    }

    api_url = "https://api.crossref.org/works?"
    params = {"rows": str(max_results),
              "query.author": author_name,
              "query.affiliation": "British Columbia"}
    url = api_url + urlencode(params, quote_via=quote_plus)

    request = Request(url)
    request.add_header("User-Agent",
                       "OpenAPC DOI Importer (https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py; mailto:openapc@uni-bielefeld.de)")
    full_data = None
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content)
        items = data["message"]["items"]

        filtered_items = []
        for item in items:
            try:
                paper_authors = ["{} {}".format(a["given"], a["family"]) for a in item['author']]
                if max([ratio(a, author_name) for a in paper_authors]) >= sim_threshold:
                    filtered_items.append(item)
            except:
                pass

        return filtered_items
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}


if __name__ == '__main__':
    get_author("John S. Richardson")
    print("done")
