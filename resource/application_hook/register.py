# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import os
from ftrack_connect_pipeline_definition import collect


def collect_definitions(event):
    current_dir  = os.path.dirname(__file__)

    schemas = collect.collect_json(
        os.path.join(current_dir, 'schema')
    )

    loaders = collect.collect_json(
        os.path.join(current_dir, 'loader')
    )

    packages = collect.collect_json(
        os.path.join(current_dir, 'package')
    )

    publishers = collect.collect_json(
        os.path.join(current_dir, 'package')
    )

    result_data = {
        'schemas': schemas,
        'publishers': publishers,
        'loaders': loaders,
        'packages': packages

    }

    return result_data


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    api_object.event_hub.subscribe(
        'topic={} and data.pipeline.type=definition'.format(constants.PIPELINE_REGISTER_TOPIC),
        collect_definitions
    )
