import json
import logging
import os
from time import sleep

from colorama import Fore, Style
from scholarly import scholarly, ProxyGenerator

from futurewater.crossref import get_publication
from futurewater.util import format_author

MAX_RETRIES_ON_ERROR = 3

# https://scholarly.readthedocs.io/en/latest/quickstart.html#installation
# https://github.com/scholarly-python-package/scholarly
# https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()

pg = ProxyGenerator()
pg.Tor_External(tor_sock_port=9050, tor_control_port=9051, tor_password="scholarly_password")
scholarly.use_proxy(pg)


def get_schoolar_data(author_name, cache_folder="scholarly", affiliation='UBC'):
    output_folder = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "resources", cache_folder
    )
    cached = os.path.join(output_folder, format_author(author_name))
    from_cache = False
    final_data = []
    if not os.path.isfile(cached):

        try:
            # Retrieve the author's data, fill-in, and print
            search_query = scholarly.search_author(f'{author_name} {affiliation}')
            author = scholarly.fill(next(search_query))

            # Print the titles of the author's publications
            titles = [pub['bib']['title'] for pub in author['publications']]

            final_data = []
            for title in titles:
                logger.info("Processing " + Fore.YELLOW + title + Style.RESET_ALL)
                ret = get_publication(title)
                retries = 0
                while not ret['success'] and retries < MAX_RETRIES_ON_ERROR:
                    retries += 1
                    msg = "Error while querying CrossRef API ({}), retrying ({})...".format(ret["exception"], retries)
                    logger.info(Fore.RED + msg + Style.RESET_ALL)
                    ret = get_publication(title)
                    sleep(3)

                if ret['success']:
                    ret['original_title'] = title
                    final_data.append(ret)
                else:
                    logger.info(Fore.RED + '> Failed' + Style.RESET_ALL)

            final_data = list(filter(lambda k: k['result']['similarity'] >= 0.7, final_data))
            final_data = sorted(final_data, key=lambda k: k['result']['similarity'], reverse=True)

            with open(cached, 'w') as fo:
                json.dump(final_data, fo, indent=4, sort_keys=True)
        except StopIteration:
            logger.info(Fore.RED + 'no more schoolar data available' + Style.RESET_ALL)
            with open(cached, 'w') as fo:
                json.dump(final_data, fo, indent=4, sort_keys=True)
        except Exception as ex:
            logger.exception(str(ex))
    else:
        with open(cached, 'r') as fo:
            final_data = json.load(fo)
            from_cache = True

    return final_data, from_cache
