# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json
from functools import partial
import logging


_package_component_schema = {
    "title": "PackageComponent",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "name"
    ],
    "properties": {
        "name": {"type": "string"},
        "file_type": {"type": "array", "items":{"type": "string"}},
        "optional": {"type": "boolean"}
    }
}

def register_package_schema(session, event):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # return json so we can validate it
    _context_types = [str(t["name"]) for t in session.query("ObjectType").all()]
    _asset_types = list(set([str(t["short"]) for t in session.query("AssetType").all()]))

    logger.debug("_context_types --> {}".format(_context_types))
    logger.debug("_asset_types --> {}".format(_asset_types))

    return json.dumps(
        {
            "title": "Package",
            "type": "object",
            "additionalProperties": False,
            "definitions": {
                'PackageComponent': _package_component_schema,
            },
            "required": [
                "name", "type", "context", "components"
            ],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string", "enum": _asset_types},
                constants.CONTEXT: {
                    "type": "array",
                    'minItems': 1,
                    "items": {
                        "type": "string",
                        "enum": _context_types
                    }
                },
                constants.COMPONENTS: {
                    "type": "array",
                    "items": {"$ref": "#/definitions/PackageComponent"},
                    'minItems': 1
                },
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
        'topic={} and data.pipeline.type={}'.format(constants.PIPELINE_REGISTER_TOPIC, constants.PACKAGE_SCHEMA),
        partial(register_package_schema, api_object)
    )