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

_component_schema = {
    "title": "Component",
    "type": "object",
    "required": [
        "name"
    ],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        constants.COLLECT: {
            "type": "array",
            "items": {"$ref": "#/definitions/Plugin"},
            "default": [],
            'minItems': 0,
            'uniqueItems': True
        },
        constants.VALIDATE: {
            "type": "array",
            "items": {"$ref": "#/definitions/Plugin"},
            "default": [],
            'minItems': 0,
            'uniqueItems': True
        },
        constants.OUTPUT: {
            "type": "array",
            "items": {"$ref": "#/definitions/Plugin"},
            "default": [],
            'minItems': 0,
            'uniqueItems': True
        },
    }
}

def register_publisher_schema(event):
    # return json so we can validate it
    return json.dumps(
        {
            "title": "Publisher",
            "type": "object",
            "additionalProperties": False,
            "definitions": {
                'Component': _component_schema,
                'Plugin': _plugin_schema
            },
            "required": [
                "name", "package", "host", "ui", "context", "components", "publishers"
            ],
            "properties": {
                "name": {"type": "string"},
                "package": {"type": "string"},
                "host": {"type": "string"},
                "ui": {"type": "string"},
                constants.CONTEXT: {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Plugin"},
                    "default": [],
                    "minItems": 0,
                    "maxItems": 1,
                },
                constants.COMPONENTS: {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Component"},
                    "default": [],
                    'minItems': 0,
                    'uniqueItems': True
                },
                constants.PUBLISH: {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Plugin"},
                    'minItems': 1,
                    'uniqueItems': True
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
        'topic={} and data.pipeline.type={}'.format(constants.PIPELINE_REGISTER_TOPIC, constants.PUBLISHER_SCHEMA),
        register_publisher_schema
    )