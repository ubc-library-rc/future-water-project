# Ryan Ziels, Civil Engineering
# https://orcid.org/0000-0003-3705-6078


# Ali Ameli, Earth, Ocean and Atmospheric Sciences
# https://orcid.org/0000-0002-8173-887X

# curl https://api.crossref.org/works?filter=has-orcid:true,orcid:0000-0002-8173-887X&mailto=msarthur@cs.ubc.ca | json_pp
# curl https://www.wikidata.org/w/api.php\?search\=Ali+Ameli\&action\=wbsearchentities\&language\=en\&uselang\=en\&format\=json\&strictlanguage\=true\&_\=1616186158210  | json_pp
# TODO: get publications after getting OCRID


# https://api.crossref.org/works?query.author=ali+a.+ameli&mailto=msarthur@cs.ubc.ca&filter=from-pub-date:2014-03-03,until-pub-date:2020-03-19&sample=30

from __future__ import print_function

import logging

import requests

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()

HEADERS = {
    'User-Agent': 'Scholia',
}

# Must be indexed from zero
MONTH_NUMBER_TO_MONTH = {
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July',
           'August', 'September', 'October', 'November', 'December']
}


def get_orcid(description):
    if 'ORCID ID' in description:
        return description.split('=', 1)[-1].strip()
    return None


def wb_get_entities(qs):
    if not qs:
        return {}

    if len(qs) > 50:
        raise NotImplementedError("Cannot handle over 50 qs yet")

    ids = "|".join(qs)
    params = {
        'action': 'wbgetentities',
        'ids': ids,
        'format': 'json',
    }
    headers = {
        'User-Agent': 'Scholia',
    }
    response_data = requests.get(
        'https://www.wikidata.org/w/api.php',
        headers=headers, params=params).json()
    if 'entities' in response_data:
        return response_data['entities']

    # TODO: Make informative/better error handling
    if 'error' in response_data:
        message = response_data['error'].get('info', '')
        message += ", id=" + response_data['error'].get('id', '')
        raise Exception(message)

    # Last resort
    raise Exception('API error')


def search_author(author):
    if not author:
        return {}

    params = {
        'action': 'wbsearchentities',
        'search': author,
        'language': 'en',
        'uselang': 'en',
        'format': 'json',
    }
    headers = {
        'User-Agent': 'Scholia',
    }
    response_data = requests.get(
        'https://www.wikidata.org/w/api.php',
        headers=headers, params=params).json()
    if 'search' in response_data:
        if response_data['search']:
            return [
                dict(wikidata_id=d['id'],
                     orcid=get_orcid(d['description'])) for d in response_data['search']
            ]
        else:
            return None

    if 'error' in response_data:
        message = response_data['error'].get('info', '')
        message += ", id=" + response_data['error'].get('id', '')
        raise Exception(message)

    # Last resort
    raise Exception('API error')


def __get_values_for_property(value):
    result = []
    for v in value:
        result.append(v['mainsnak']['datavalue']['value'])

    if len(result) == 1:
        return next(iter(result))
    else:
        return result


def get_publication_details(wikidata_id):
    query = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json?"
    params = {
        'language': 'en',
        'uselang': 'en',
        'format': 'json',
    }
    headers = {
        'User-Agent': 'Scholia',
    }
    response_data = requests.get(
        query,
        headers=headers, params=params).json()
    label_of = {
        'P1476': 'title',
        'P2093': 'author_name',
        'P577': 'publication_date',
        'P304': 'pages',
        'P433': 'issue',
        'P356': 'DOI',
        'P921': 'topics'
    }

    if 'error' in response_data:
        message = response_data['error'].get('info', '')
        message += ", id=" + response_data['error'].get('id', '')
        raise Exception(message)
    result = None
    if 'entities' in response_data:
        result = response_data['entities'][wikidata_id]
    claim = [(key, __get_values_for_property(value)) for key, value in result['claims'].items()]
    del result['claims']
    for key, value in claim:
        if key in label_of:
            if key == 'P921' and not isinstance(value, list):
                result[label_of[key]] = list(value)
            else:
                result[label_of[key]] = value
    return result


def get_topic_details(wikidata_id, recursive=True):
    query = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json?"
    params = {
        'language': 'en',
        'uselang': 'en',
        'format': 'json',
    }
    headers = {
        'User-Agent': 'Scholia',
    }
    label_of = {
        'P279': 'subclass_of',
        'P1269': 'facet_of',
    }

    response_data = requests.get(
        query,
        headers=headers, params=params).json()

    if 'error' in response_data:
        message = response_data['error'].get('info', '')
        message += ", id=" + response_data['error'].get('id', '')
        raise Exception(message)
    result = None
    if 'entities' in response_data:
        result = response_data['entities'][wikidata_id]
        result = dict(
            id=result['id'],
            topic=result['labels']['en']['value']
        )

    return result


def get_publications(wikidata_id):
    query = f"""
        SELECT
          (MIN(?dates) AS ?date)
          ?work ?workLabel
          (GROUP_CONCAT(DISTINCT ?type_label; separator=", ") AS ?type)
          (SAMPLE(?pages_) AS ?pages)
          ?venue ?venueLabel
          (GROUP_CONCAT(DISTINCT ?author_label; separator=", ") AS ?authors)
          (CONCAT("../authors/", GROUP_CONCAT(DISTINCT SUBSTR(STR(?author), 32); separator=",")) AS ?authorsUrl)
        WHERE {{
          ?work wdt:P50 wd:{wikidata_id} .
          ?work wdt:P50 ?author .
          OPTIONAL {{
            ?author rdfs:label ?author_label_ . FILTER (LANG(?author_label_) = 'en')
          }}
          BIND(COALESCE(?author_label_, SUBSTR(STR(?author), 32)) AS ?author_label)
          OPTIONAL {{ ?work wdt:P31 ?type_ . ?type_ rdfs:label ?type_label . FILTER (LANG(?type_label) = 'en') }}
          ?work wdt:P577 ?datetimes .
          BIND(xsd:date(?datetimes) AS ?dates)
          OPTIONAL {{ ?work wdt:P1104 ?pages_ }}
          OPTIONAL {{ ?work wdt:P1433 ?venue }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,da,de,es,fr,jp,no,ru,sv,zh". }}  
        }}
        GROUP BY ?work ?workLabel ?venue ?venueLabel
        ORDER BY DESC(?date)  
    """

    url = 'https://query.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    results = data['results']['bindings']
    if results:
        return [r['work']['value'].replace('http://www.wikidata.org/entity/', '') for r in results]
    else:
        return None


def entity_to_name(entity):
    if 'labels' in entity:
        labels = entity['labels']
        if 'en' in labels:
            return labels['en']['value']
        else:
            for label in labels.values():
                return label['value']
    return None
