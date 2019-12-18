# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging
import ftrack_api
import functools
from ftrack_connect_pipeline_definition import collect, validate
from ftrack_connect_pipeline import constants, configure_logging

logger = logging.getLogger('ftrack_connect_pipeline_definition.register')


def register_definitions(session, event):
    current_dir = os.path.dirname(__file__)
    # collect definitions
    data = collect.collect_definitions(current_dir)

    # filter definitions
    host = event['data']['pipeline']['host']
    data = collect.filter_definitions_by_host(data, host)

    # validate schemas
    data = validate.validate_schema(data)

    # validate asset types
    data = validate.validate_asset_types(data, session)

    # validate packages
    data = validate.validate_package_type(data)

    # validate packages
    data = validate.validate_definition_components(data)

    # log final discovery result
    for key, value in data.items():
        logger.info('discovered : {} : {}'.format(key, len(value)))

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
