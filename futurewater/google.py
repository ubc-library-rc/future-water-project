from scholarly import scholarly, ProxyGenerator
from time import sleep
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request
import json
from colorama import Fore, Back, Style
from Levenshtein import ratio, matching_blocks, editops

EMPTY_RESULT = {
    "crossref_title": "",
    "similarity": 0,
    "doi": ""
}

MAX_RETRIES_ON_ERROR = 3

# https://scholarly.readthedocs.io/en/latest/quickstart.html#installation
# https://github.com/scholarly-python-package/scholarly
# https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py

def crossref_query_title(title):
    api_url = "https://api.crossref.org/works?"
    params = {"rows": "5", "query.bibliographic": title}
    url = api_url + urlencode(params, quote_via=quote_plus)
    print(url)
    request = Request(url)
    request.add_header("User-Agent", "OpenAPC DOI Importer (https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py; mailto:openapc@uni-bielefeld.de)")
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
        return {"success": True, "result": most_similar}
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}


pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)


# Retrieve the author's data, fill-in, and print
search_query = scholarly.search_author('Ali Ameli UBC')
author = scholarly.fill(next(search_query))
print(author)

# Print the titles of the author's publications
titles = [pub['bib']['title'] for pub in author['publications']]

final_data = []
for title in titles:
    print("Processing " + Fore.YELLOW + title + Style.RESET_ALL)
    ret = crossref_query_title(title)
    retries = 0
    while not ret['success'] and retries < MAX_RETRIES_ON_ERROR:
        retries += 1
        msg = "Error while querying CrossRef API ({}), retrying ({})...".format(ret["exception"], retries)
        print(Fore.RED + msg + Style.RESET_ALL)
        ret = crossref_query_title(title)
        sleep(3)

    ret['original_title'] = title
    final_data.append(ret)
    # break

final_data = list(filter(lambda k: k['result']['similarity'] >= 0.7, final_data))

print(json.dumps(final_data, indent=4, sort_keys=True))


