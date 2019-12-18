# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging
import ftrack_api
import functools
from ftrack_connect_pipeline_definition import collect
from ftrack_connect_pipeline import constants

logger = logging.getLogger(__name__)


def register_definitions(session, event):
    host = event['data']['pipeline']['host']
    current_dir = os.path.dirname(__file__)
    result_data = collect.collect_and_filter_definitions(session, current_dir, host)
    return result_data


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
