# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import glob
import logging

def collect_json(sourcePath, event):
    logger = logging.getLogger(__name__)
    jsonFiles_l = glob.glob(sourcePath + '/*.json')
    loadedJsons_l = []
    for file_s in jsonFiles_l:
        with open(file_s, 'r') as f:
            try:
                datastore = json.load(f)
            except Exception as e:
                logger.warning("{0} could not be registered, reason: {1}".format(file_s, e))

        loadedJsons_l.append(datastore)

    return json.dumps(loadedJsons_l)
