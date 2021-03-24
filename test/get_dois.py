from scholarly import ProxyGenerator
from scholarly import scholarly
import time


def search(titles):
    for t in titles:
        time.sleep(2)
        query = scholarly.search_pubs(t)
        if not query:
            continue
        pub = next(query)
        if pub:
            scholarly.bibtex(pub)


def main():
    search_query = scholarly.search_author('Ali Ameli, UBC')
    author = scholarly.fill(next(search_query))
    titles = [pub['bib']['title'] for pub in author['publications']]
    search(titles)


if __name__ == '__main__':
    main()
