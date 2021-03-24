from __future__ import print_function

import logging

import requests

# https://stackoverflow.com/questions/11029717/how-do-i-disable-log-messages-from-the-requests-library
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()


def get_publications(ocrid, dois=None):
    if not dois:
        dois = []
    query = f"https://api.crossref.org/works?filter=has-orcid:true,orcid:{ocrid}&mailto=msarthur@cs.ubc.ca"
    headers = {
        'User-Agent': 'Scholia',
    }
    response_data = requests.get(
        query,
        headers=headers).json()

    # FIXME: needs pagination
    if response_data and 'message' in response_data:
        return [item for item in response_data['message']['items'] if item['DOI'] not in dois]
    return None
