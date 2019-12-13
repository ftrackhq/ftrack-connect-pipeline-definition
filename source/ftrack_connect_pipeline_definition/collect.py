# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import fnmatch
import os
import logging

logger = logging.getLogger(__name__)


def collect_json(source_path):
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

        if data_store:
            loaded_jsons.append(data_store)

    return loaded_jsons
