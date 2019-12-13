# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import glob
import logging

logger = logging.getLogger(__name__)


def collect_json(source_path, event):
    '''
    Return a json encoded list of all the json files discovered in the given
    *source_path*.
    '''

    json_files = glob.glob(source_path + '/*.json')
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

    return json.dumps(loaded_jsons)
