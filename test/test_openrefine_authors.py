from __future__ import print_function

import csv
import json
import logging
import os
import sys

from futurewater.util import format_author

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
            new_entry = dict(
                Len=data['author'],
                P31='Q5',  # instance of = human
                P106='Q1650915',  # occupation = researcher
                P463='Q106489997',  # member of = Future Water Cluster
                P2561=data['author'],  # name
            )
            result.append(new_entry)

    return result


def write_output_file(data):
    if not data:
        return
    keys = data[0].keys()
    _output = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'imports', 'open_refine_authors.csv'
    )

    with open(_output, 'w', newline='') as output_file:
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

    write_output_file(final_data)


if __name__ == '__main__':
    main()
