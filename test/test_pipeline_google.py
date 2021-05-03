from __future__ import print_function

import csv
import logging
import os
import sys
import time

from colorama import Fore, Style

# adding path to run files from root when in docker container
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import futurewater.google as google_api

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def main(throttling_delay=5):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    _input = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'cluster-members.csv'
    )

    authors = []
    with open(_input) as _f:
        _data = csv.DictReader(_f)
        for row in _data:
            authors.append((row['Full Name'], row['Affiliation']))

    all = []
    for author_name, affiliation in authors:
        logger.info('Processing' + Fore.YELLOW + f' {author_name}' + Style.RESET_ALL)
        try:
            cross_ref, from_cache = google_api.get_schoolar_data(author_name, affiliation=affiliation)
            all.append(cross_ref)
            if not from_cache:
                logger.info(
                    Fore.RED + f'Sleeping {throttling_delay}s to avoid throttling/IP blocking' + Style.RESET_ALL)
                time.sleep(throttling_delay)  # throttling
        except Exception:
            logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
            logging.exception("message")

    has_data = list(filter(lambda k: k, all))
    logger.info(f"{str(len(has_data))} out of the {str(len(all))} authors in the cluster were successfully processed")


if __name__ == '__main__':
    logger.info("Fetching resources from Google Scholar")
    main()
    logger.info(">> Output at " + Fore.RED + "./resources/scholarly" + Style.RESET_ALL)
    logger.info('-' * 10)
    logger.info('-' * 10)
