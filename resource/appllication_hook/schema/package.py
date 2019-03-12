# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline_definition import schema
import json


def register_asset_schema(event):

    # return json so we can validate it
    return json.dumps(
         schema.asset_schema
    )


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register_assets is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    api_object.event_hub.subscribe(
        'topic={} and data.pipeline.type=package_schema'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_asset_schema
    )
