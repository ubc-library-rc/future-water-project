from __future__ import print_function

import json
import logging
import os
import sys

from colorama import Fore, Style

import futurewater.crossref as crossref_api
import futurewater.wikidata as wikidata_api

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


def water_info(author_name, test=False):
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
            if len(author_data) > 1:
                logger.info(Fore.RED + f'Author {author_name} requires disambiguation' + Style.RESET_ALL)
                logger.info(json.dumps(author_data, indent=4, sort_keys=True))
                return

            author = next(iter(author_data))
            author['name'] = author_name

            logger.info("Fetching existing publications on " + Fore.YELLOW + 'Wikidata' + Style.RESET_ALL)
            publication_wiki_ids = wikidata_api.get_publications(author['wikidata_id'])
            publication_wiki_ids = ['Q15708879']
            wikidata = []
            dois = set()
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
            missing_wikidata = [] # crossref_api.get_publications(author['orcid'], dois=dois)
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
    water_info('Emily Lundt', test=True)

    # _input = os.path.join(
    #     os.path.dirname(os.path.realpath(__file__)),
    #     '..', 'resources', 'cluster-members.csv'
    # )
    #
    # authors = []
    # with open(_input) as _f:
    #     _data = csv.DictReader(_f)
    #     for row in _data:
    #         authors.append(row['\ufeffFull Name'])
    #
    # for author_name in authors:
    #     try:
    #         water_info(author_name)
    #         time.sleep(throttling_delay)
    #         logger.info(Fore.RED + f'Sleeping {throttling_delay}s to avoid throttling/IP blocking' + Style.RESET_ALL)
    #     except Exception:
    #         logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
    #         logging.exception("message")


if __name__ == '__main__':
    main()
