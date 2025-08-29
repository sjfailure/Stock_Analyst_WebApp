import logging
import os
from pathlib import Path


def get_file_contents(filename):
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
       logging.error("'%s' file not found" % filename)


api_file = os.path.join(Path(__file__).resolve().parent.parent, 'model/apikey')

def get_api_key(file=api_file):
    return get_file_contents(file)