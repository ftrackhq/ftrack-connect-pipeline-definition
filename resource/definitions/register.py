# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging
import ftrack_api
import functools
from ftrack_connect_pipeline import constants, configure_logging
import ftrack_connect_pipeline.definition

logger = logging.getLogger('ftrack_connect_pipeline_definition.register')


def register_definitions(session, event):
    host_types = event['data']['pipeline']['host_types']
    current_dir = os.path.dirname(__file__)
    # collect definitions
    data = ftrack_connect_pipeline.definition.collect_and_validate(
        session, current_dir, host_types
    )
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
        callback,
    )
