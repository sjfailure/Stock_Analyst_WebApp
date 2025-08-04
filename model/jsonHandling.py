import json
import logging


def save_to_file(json_data, filename=None):
    if filename is None:
        filename = '/current_data.json'
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    logging.debug('json file written to HD for later')
    return
