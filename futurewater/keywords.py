import os

keywords = []
with open(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'resources', 'keywords.csv'
), "r") as f:
    keywords = f.read().splitlines()
    keywords = [k.lower().strip() for k in keywords]
    keywords = sorted(keywords)


def get_publication_subject(author_name, publication_data, title=None):
    if not title:
        title = ""
    abstract = ""
    if "abstract" in publication_data:
        abstract = publication_data['abstract']
    subject = []
    if 'subject' in publication_data:
        subject = publication_data['subject']
        subject = [k.lower().strip() for k in subject]

    matched_keywords = list()
    matched_keywords += match(keywords, subject)
    matched_keywords += match(keywords, title.lower())
    matched_keywords += match(keywords, abstract.lower())

    matched_keywords = list(filter(lambda k: k is not None, matched_keywords))

    if matched_keywords:
        return next(iter(matched_keywords))

    if subject:
        return next(iter(subject))

    return None


def match(lst, input):
    result = set()
    if not lst:
        return list(result)

    if not input:
        return list(result)

    for idx, element in enumerate(lst):
        if element in input:
            result.add(element)

    return list(result)

    # if subject and any(x in keywords for x in subject):
    #     return True
    #
    # if any(x in keywords for x in title.split()):
    #     return True
    #
    # if abstract and any(x in keywords for x in abstract.split()):
    #     return True

    return False
