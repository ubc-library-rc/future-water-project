from __future__ import print_function

import json
import logging
import os
import sys
import time
import csv

from colorama import Fore, Style

import futurewater.crossref as crossref_api
import futurewater.wikidata as wikidata_api
from futurewater.disambiguation import disambiguate

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def format_author(name):
    aux = "_".join([n.lower() for n in name.split(" ")])
    return f"{aux}.json"


def publications_info(author_name, wikidata_id, test=False):
    if wikidata_id == "":
        wikidata_id = None
    output_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources", "wikidata"
    )
    cached = os.path.join(output_folder, format_author(author_name))



    if not os.path.isfile(cached):
        logger.info('Processing' + Fore.YELLOW + f' {author_name}' + Style.RESET_ALL)
        logger.info("Fetching author " + Fore.YELLOW + 'WikidataID/OCRID' + Style.RESET_ALL)
        author_data = wikidata_api.search_author(author_name)

        if author_data:
            if wikidata_id:
                author_data = list(filter(lambda k: wikidata_id == k['wikidata_id'], author_data))

            if len(author_data) > 1:
                # potential_wiki_ids = disambiguate(author_name)
                # if len(potential_wiki_ids) == 1:
                #     wiki_id = next(iter(potential_wiki_ids))
                #     author_data = list(filter(lambda k: wiki_id == k['wikidata_id'], author_data))
                # else:
                logger.info(Fore.RED + f'Author {author_name} requires disambiguation' + Style.RESET_ALL)
                logger.info(json.dumps(author_data, indent=4, sort_keys=True))
                return

            author = next(iter(author_data))
            author['name'] = author_name

            logger.info("Fetching existing publications on " + Fore.YELLOW + 'Wikidata' + Style.RESET_ALL)
            publication_wiki_ids = wikidata_api.get_publications(author['wikidata_id'])
            wikidata = []
            dois = set()
            if publication_wiki_ids:
                for wikidata_id in publication_wiki_ids:
                    entity = wikidata_api.get_publication_details(wikidata_id)
                    if entity:
                        if 'topics' in entity:
                            detailed_topics = [wikidata_api.get_topic_details(t['id']) for t in entity['topics']]
                            entity['topics'] = detailed_topics

                        wikidata.append(entity)
                        if 'DOI' in entity:
                            dois.add(entity['DOI'])

            logger.info("Fetching missing wikidata using " + Fore.YELLOW + 'CrossRef' + Style.RESET_ALL)
            missing_wikidata = []

            if author['orcid']:
                missing_wikidata = crossref_api.get_publications(author['orcid'], dois=dois)
            else:
                logger.info(Fore.RED + f'{author_name} does not have a orcid to fetch data from crossref' + Style.RESET_ALL)
            # missing_wikidata = [dict(doi=d['DOI'], title=d['title']) for d in missing_wikidata]
            # print(json.dumps(missing_wikidata, indent=4, sort_keys=True))

            final_data = dict(
                author=author,
                wikidata=wikidata,
                missing_data=missing_wikidata
            )

            if not test:
                with open(cached, 'w') as fo:
                    json.dump(final_data, fo, indent=4, sort_keys=True)
        else:
            logger.info(Fore.RED + f'Author {author_name} not available on Wikidata' + Style.RESET_ALL)

    else:
        logger.info(Fore.YELLOW + f'loaded {author_name} from cache' + Style.RESET_ALL)


def main(throttling_delay=3):
    # publications_info('Ali Ameli', test=True) # OK
    # publications_info('Alice Guimaraes', test=True)
    # publications_info('Jongho Lee', test=True)
    # publications_info('Jordi Honey-Rosés', test=True)
    # publications_info('Jordi Honey-Rosés', test=True)
    # publications_info('Jordi Honey-Rosés', test=True)
    # publications_info('Jordi Honey-Rosés', test=True)



    # FIXME: uncomment as soon as I get it to work for a good portion of the cluster members
    _input = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'cluster-members.csv'
    )

    authors = []
    with open(_input) as _f:
        _data = csv.DictReader(_f)
        for row in _data:
            authors.append((row['Full Name'], row['wikidata']))

    for author_name, wiki_id in authors:
        try:
            publications_info(author_name, wikidata_id=wiki_id)
            time.sleep(throttling_delay)
            logger.info(Fore.RED + f'Sleeping {throttling_delay}s to avoid throttling/IP blocking' + Style.RESET_ALL)
        except Exception:
            logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
            logging.exception("message")
    # TODO: find how to dumb missing items into wikidata
    # TODO: find how to update project members to be part of the research cluster


if __name__ == '__main__':
    main()
