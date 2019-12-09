# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


_plugin_schema = {
    "title":"Plugin",
    "type": "object",
    "required": [
        "name", "plugin"
    ],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "plugin": {"type": "string"},
        "widget": {"type": "string"},
        "visible": {"type": "boolean"},
        "editable": {"type": "boolean"},
        "disabled": {"type": "boolean"},
        "options": {"type": "object"},

    }
}

def register_loader_schema(event):
    # return json so we can validate it
    return json.dumps(
        {
            "title": "Loader",
            "additionalProperties": False,
            "required": [
                "host", "ui"
            ],
            "properties": {
                "name": {"type": "string"},
                "host": {"type": "string"},
                "ui": {"type": "string"},
                constants.COMPONENTS: {
                    "type": "array",
                    "items": _plugin_schema
                },
                "post": {
                    "type": "array",
                    "items": _plugin_schema
                }
            }
        }
    )


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    api_object.event_hub.subscribe(
        'topic={} and data.pipeline.type={}'.format(constants.PIPELINE_REGISTER_TOPIC, constants.LOADER_SCHEMA),
        register_loader_schema
    )