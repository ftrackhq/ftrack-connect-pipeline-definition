# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import fnmatch
import os
import logging
from jsonschema import validate as _validate

logger = logging.getLogger(__name__)


def collect_json(source_path, filter_host=None):
    '''
    Return a json encoded list of all the json files discovered in the given
    *source_path*.
    '''

    json_files = []
    for root, dirnames, filenames in os.walk(source_path):
        for filename in fnmatch.filter(filenames, '*.json'):
            json_files.append(os.path.join(root, filename))

    loaded_jsons = []
    for json_file in json_files:
        data_store = None
        with open(json_file, 'r') as _file:
            try:
                data_store = json.load(_file)
            except Exception as error:
                logger.warning(
                    "{0} could not be registered, reason: {1}".format(
                        _file, str(error)
                    )
                )

        if filter_host:
            if data_store.get('host') != filter_host:
                continue

        if data_store:
            loaded_jsons.append(data_store)

    return loaded_jsons


def validate(schema, definition):
    '''Validate all the given definitions with the given schema'''
    try:
        _validate(instance=definition, schema=schema)
    except Exception as error:
        print error
        return False

    return True
