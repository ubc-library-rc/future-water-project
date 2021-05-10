from __future__ import print_function

import csv
import json
import logging
import os
import sys
# adding path to run files from root when in docker container
from collections import defaultdict, Counter

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from colorama import Fore, Style

from futurewater.keywords import get_publication_subject
from futurewater.util import format_author

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)



def load_google_data(author_file, resources_folder, scholarly_folder="scholarly"):
    logger.info("\tFetching publications on " + Fore.YELLOW + 'Google Scholarly' + Style.RESET_ALL)
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


def wikidata_keywords(author_name, keyword_authors, authors_keywords):
    resources_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources"
    )

    author_file = format_author(author_name)
    resources_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources"
    )

    gdata = load_google_data(author_file, resources_folder)

    for row in gdata:
        try:
            title = None
            if row['title']:
                title = next(iter(row['title']))
            if not title and 'original_title' in row:
                title = row['original_title']

            if not title:
                continue

            main_subject = get_publication_subject(author_name, row, title=title)  # main subject,
            if not main_subject:
                continue

            for keyword in main_subject:
                keyword_authors[keyword].append(author_name)
                authors_keywords[author_name].append(keyword)

        except Exception as ex:
            logger.exception(ex)


def write_output_file(keyword_authors, authors_keywords, file_name, max_keywords=10):
    _output = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', )

    _output = os.path.join(_output, f'{file_name}.json')

    for author in authors_keywords.keys():
        most_prominent = [{'topicLabel': k, 'score': c} for k, c in Counter(authors_keywords[author]).most_common(max_keywords)]
        authors_keywords[author] = most_prominent

    for keyword in keyword_authors.keys():
        most_prominent = [{'topicLabel': k, 'score': c} for k, c in Counter(keyword_authors[keyword]).most_common()]
        keyword_authors[keyword] = most_prominent

    with open(_output, "w") as outfile:
        json.dump({
            "keywords": keyword_authors,
            "authors": authors_keywords,
        }, outfile, indent=4)


def main():
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

    keyword_authors = defaultdict(list)
    authors_keywords = defaultdict(list)
    for author_name in authors:
        try:
            wikidata_keywords(author_name, keyword_authors, authors_keywords)
        except Exception as ex:
            logger.exception(ex)

    write_output_file(
        keyword_authors, authors_keywords,
        'keywords_final'
    )


if __name__ == '__main__':
    logger.info("\n\nWriting scholia " + Fore.YELLOW + " keywords " + Style.RESET_ALL + " in the cluster")
    main()
    logger.info(
        ">> " + Fore.YELLOW + "Scholia" + Style.RESET_ALL + " output at " + Fore.RED + "./resources/keywords_final.json" + Style.RESET_ALL)
    logger.info('-' * 10)
    logger.info('-' * 10)
