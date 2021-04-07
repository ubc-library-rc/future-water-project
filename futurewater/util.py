def format_author(name):
    aux = "_".join([n.lower() for n in name.split(" ")])
    return f"{aux}.json"


def to_quickstatements_format(input):
    input = input.replace('"', '""')
    return input
