from __future__ import print_function

import csv
import json
import logging
import os
import sys
import time

from Levenshtein import ratio
from colorama import Fore, Style

# adding path to run files from root when in docker container
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import futurewater.wikidata as wikidata_api
from futurewater.util import format_author

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def load_crossref_data(author_file, resources_folder, crossref_folder="crossref"):
    input_path = os.path.join(resources_folder, crossref_folder, author_file)
    if not os.path.isfile(input_path):
        return []

    with open(input_path, 'r') as fo:
        aux = json.load(fo)
        for a in aux:
            a['source'] = crossref_folder
        return aux


def load_google_data(author_file, resources_folder, scholarly_folder="scholarly"):
    input_path = os.path.join(resources_folder, scholarly_folder, author_file)
    if not os.path.isfile(input_path):
        return []

    with open(input_path, 'r') as fo:
        data = json.load(fo)
        aux = [d['crossref'] for d in data if 'crossref' in d]
        for a, d in zip(aux, data):
            a['source'] = scholarly_folder
            a['original_title'] = d['original_title']
        return aux


def merge_sources(google_data, crossref_data):
    doi_publication_map = {}
    for source in [google_data, crossref_data]:
        for data in source:
            if "DOI" not in data:
                continue
            doi_publication_map[data["DOI"]] = data

    return doi_publication_map.values()


def get_wikidata_author_id(author_name, wikidata):
    if wikidata:
        author_list = [(a['authors'], a['authorsurl']) for a in wikidata if 'authorsurl' in a]
        for author, url in author_list:
            for author_wikidata_name, author_wikidata_url in zip(author.split(","), url.split(",")):
                if ratio(author_wikidata_name, author_name) >= 0.85:
                    author_wikidata_id = author_wikidata_url.split('/')[-1]
                    return author_wikidata_id
    return None


def get_wikidata_detailed_publications(wikidata_lst):
    detailed_wikidata_lst = []
    for wikidata_summary in wikidata_lst:
        logger.info("\t\tFetching details of publication " + Fore.YELLOW + wikidata_summary['doi'] + Style.RESET_ALL)
        wikidata_summary['work'] = wikidata_summary['work'].split('/')[-1]
        entity = wikidata_api.get_publication_details(wikidata_summary['work'])
        if entity:
            if 'topics' in entity:
                try:
                    detailed_topics = [wikidata_api.get_topic_details(t['id']) for t in entity['topics']]
                    entity['topics'] = detailed_topics
                except:
                    pass

            detailed_wikidata_lst.append(entity)
    return detailed_wikidata_lst


def publications_info(author_name, test=False):
    logger.info('Processing' + Fore.YELLOW + f' {author_name}' + Style.RESET_ALL)

    resources_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources"
    )
    author_file = format_author(author_name)
    output_folder = os.path.join(resources_folder, "wikidata")
    cached = os.path.join(output_folder, author_file)

    publication_lst = merge_sources(
        load_google_data(author_file, resources_folder),
        load_crossref_data(author_file, resources_folder)
    )

    if not os.path.isfile(cached):
        logger.info("\tFetching publications on " + Fore.YELLOW + 'Wikidata' + Style.RESET_ALL)

        in_wikidata, not_in_wikidata = [], []
        for publication in publication_lst:
            data = wikidata_api.get_publication(publication["DOI"])
            if data:
                in_wikidata.append(data)
            else:
                not_in_wikidata.append(publication)

        author_wikidata_id = get_wikidata_author_id(author_name, in_wikidata)
        detailed_wikidata_lst = get_wikidata_detailed_publications(in_wikidata)

        final_data = dict(
            author=author_name,
            wikidata_id=author_wikidata_id,
            wikidata=detailed_wikidata_lst,
            missing_data=not_in_wikidata
        )

        if not test:
            with open(cached, 'w') as fo:
                json.dump(final_data, fo, indent=4, sort_keys=True)
    else:
        logger.info(Fore.YELLOW + '\talready on cache' + Style.RESET_ALL)


def main(throttling_delay=3):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    _input = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'cluster-members.csv'
    )

    authors = []
    with open(_input) as _f:
        _data = csv.DictReader(_f)
        for row in _data:
            authors.append(row['Full Name'])

    for author_name in authors:
        try:
            publications_info(author_name, test=False)
            time.sleep(throttling_delay)
            logger.info(Fore.RED + f'Sleeping {throttling_delay}s to avoid throttling/IP blocking' + Style.RESET_ALL)
        except Exception:
            logger.error(Fore.RED + f'Error fetching data for {author_name}' + Style.RESET_ALL)
            logging.exception("message")


if __name__ == '__main__':
    logger.info("Fetching resources from Wikidata")
    main()
    logger.info(">> Output at " + Fore.RED + "./resources/wikidata" + Style.RESET_ALL)
    logger.info('-' * 10)
    logger.info('-' * 10)
