from __future__ import print_function

import json
import logging
import os
import sys
import time
import csv

from colorama import Fore, Style
from Levenshtein import ratio, matching_blocks, editops

import numpy as np
import futurewater.crossref as crossref_api
import futurewater.wikidata as wikidata_api
from futurewater.disambiguation import disambiguate
from futurewater.util import format_author, to_quickstatements_format
from futurewater.keywords import get_publication_subject

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

def wikidata_import(author_name, test=False):

    resources_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources"
    )
    author_file = format_author(author_name)
    output_folder = os.path.join(resources_folder, "wikidata")
    cached = os.path.join(output_folder, author_file)

    result = []
    if os.path.isfile(cached):
        with open(cached) as fo:
            data = json.load(fo)
            # for row in data['wikidata']:
            #     result.append(('WIKIDATA', data['author'], data['wikidata_id'], row['DOI'], row['title']['text'], row['id']))
            for row in data['missing_data']:
                try:
                    if row['title']:
                        title = next(iter(row['title']))
                        # Dictionary sorted by properties
                        new_entry = dict(
                            qid='', # empty because these are entries for missing wikidata
                            Len=to_quickstatements_format(title),
                            P31='Q13442814',  # instance of = scholarly article,
                            P50=data['wikidata_id'] if data['wikidata_id'] else data['author'],  # author
                            P356=row['DOI'], # DOI
                            P921=get_publication_subject(author_name, row), # main subject,
                            P1476 = to_quickstatements_format(title),  # title
                        )
                        result.append(new_entry)
                except Exception as ex:
                    logger.exception(ex)
                # print(row)

    return result

def write_output_file(data):
    if not data:
        return
    keys = data[0].keys()
    _output = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'missing_wikidata_importts.csv'
    )

    with open(_output, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys, quoting=csv.QUOTE_ALL)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def main():
    _input = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'cluster-members.csv'
    )

    authors = []
    with open(_input) as _f:
        _data = csv.DictReader(_f)
        for row in _data:
            authors.append((row['Full Name'], row['wikidata']))

    final_data = []
    for author_name, wiki_id in authors:
        try:
            wiki_import = wikidata_import(author_name)
            if wiki_import:
                final_data += wiki_import
        except Exception as ex:
            logger.exception(ex)

    print(json.dumps(final_data, indent=4, sort_keys=True))
    write_output_file(final_data)


if __name__ == '__main__':
    main()
