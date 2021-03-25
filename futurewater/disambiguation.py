'https://author-disambiguator.toolforge.org/?name=John+Muller&doit=Look+for+author&limit=50&filter='

from bs4 import BeautifulSoup
import abc
import logging
import os

import requests
import re



def disambiguate(author_name):
    input_name = '+'.join([w for w in author_name.split()])
    url = f'https://author-disambiguator.toolforge.org/?name={input_name}&doit=Look+for+author&limit=50&filter='
    headers = {
        'User-Agent': 'Scholia',
    }

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, features="lxml")

    authors = list(filter(lambda k: 'value' in k.attrs and k.attrs['value'].startswith('Q'), soup.findAll('input', {"type": "radio"})))

    return [a.attrs['value'] for a in authors]

