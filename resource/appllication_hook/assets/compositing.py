# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_asset(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name":"Compositing",
            "asset_type": "compPackage",
            "context":[
                "Task",
                "Compositing"
            ],
            "components":[
                {
                    "name": "script",
                    "file_type": ["nk"]
                },
                {
                    "name": "beauty",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "diffuse",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "reflection",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "shadow",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "specular",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "reviewable"
                },
                {
                    "name": "thumbnail"
                }
            ]
        }
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
        'topic={} and data.pipeline.type=asset'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_asset
    )
