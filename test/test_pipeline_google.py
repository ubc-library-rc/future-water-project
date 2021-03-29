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
import futurewater.google as google_api
from futurewater.disambiguation import disambiguate
from futurewater.util import format_author


# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)





def main(throttling_delay=10):


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
        logger.info('Processing' + Fore.YELLOW + f' {author_name}' + Style.RESET_ALL)
        try:
            cross_ref, from_cache = google_api.get_schoolar_data(author_name)
            all.append(cross_ref)
            if not from_cache:
                logger.info(
                    Fore.RED + f'Sleeping {throttling_delay}s to avoid throttling/IP blocking' + Style.RESET_ALL)
                time.sleep(throttling_delay)  # throttling
        except Exception:
            logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
            logging.exception("message")

    has_data = list(filter(lambda k: k, all))
    logger.info(f"{str(len(has_data))} out of {str(len(all))}")




if __name__ == '__main__':
    main()
