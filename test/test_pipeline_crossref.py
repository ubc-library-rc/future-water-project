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
from futurewater.util import format_author

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)





def publications_info(author_name, wikidata_id, test=False):
    if wikidata_id == "":
        wikidata_id = None
    output_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources", "crossref"
    )
    cached = os.path.join(output_folder, format_author(author_name))

    if not os.path.isfile(cached):
        logger.info('Processing' + Fore.YELLOW + f' {author_name}' + Style.RESET_ALL)
        logger.info("Fetching author " + Fore.YELLOW + 'on crossref' + Style.RESET_ALL)
        author_data = crossref_api.get_author(author_name, max_results=1000, sim_threshold=0.90)

        with open(cached, 'w') as fo:
            json.dump(author_data, fo, indent=4, sort_keys=True)
        return author_data
    else:
        logger.info(Fore.YELLOW + f'loaded {author_name} from cache' + Style.RESET_ALL)
        with open(cached, 'r') as fo:
            return json.load(fo)



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

    all = []
    for author_name, wiki_id in authors:
        try:
            data = publications_info(author_name, wikidata_id=wiki_id)
            all.append(data)
            if not data:
                logger.info(Fore.RED + f'Could not find data for {author_name}' + Style.RESET_ALL)
        except Exception:
            logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
            logging.exception("message")

    has_data = list(filter(lambda k: k, all))
    logger.info(f"{str(len(has_data))} out of {str(len(all))}")

    total = 0
    for a in has_data:
        logger.info(f"{str(len(a))}")
        total += len(a)

    logger.error(Fore.RED + f'total of {total} publications fetched' + Style.RESET_ALL)


if __name__ == '__main__':
    main()
