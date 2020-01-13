# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import json
import logging
import ftrack_api
import functools
import copy
from ftrack_connect_pipeline import constants, configure_logging
import ftrack_connect_pipeline_definition

logger = logging.getLogger('ftrack_connect_pipeline_definition.register')


def merge_extra_data(data, extra_data):
    for k in data.keys():
        data[k].extend(extra_data[k])
        set_of_jsons = {json.dumps(d, sort_keys=True) for d in data[k]}
        data[k] = [json.loads(t) for t in set_of_jsons]
    return data


def register_definitions(session, event):
    hosts = event['data']['pipeline']['host']
    current_dir = os.path.dirname(__file__)
    data = {}
    for host in hosts:
        # collect definitions
        extra_data = ftrack_connect_pipeline_definition.collect_and_validate(
            session, current_dir, host
        )
        if data:
            data = merge_extra_data(data, extra_data)
        else:
            data = copy.deepcopy(extra_data)
    for key, value in data.items():
        logger.info('Total discovered : {} : {}'.format(key, len(value)))
    return data


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    callback = functools.partial(register_definitions, api_object)

    api_object.event_hub.subscribe(
        'topic={} and data.pipeline.type=definition'.format(
            constants.PIPELINE_REGISTER_TOPIC
        ),
        callback
    )
