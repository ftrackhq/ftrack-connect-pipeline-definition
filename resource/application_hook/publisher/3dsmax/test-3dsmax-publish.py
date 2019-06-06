# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Geometry Publisher",
            "package": "geoPkg",
            "host": "3dsmax",
            "ui":"qt",
            "context":[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            "components":{
                "main":{
                    "collect":[
                        {
                            "name": "Pick selected object/s",
                            "plugin":"selection",
                        }
                    ],
                    "validate":[
                        {
                            "name": "validate selection",
                            "plugin":"nonempty"
                        }
                    ],
                    "output":[
                        {
                            "name": "3dsmaxalembic",
                            "plugin": "ExtractMaxAlembicPlugin"
                        }
                    ]
                },
                "thumbnail": {
                    "collect": [
                        {
                            "name": "select camera to playblast",
                            "plugin": "camera",
                            "options": {"camera_name": "persp"}
                        }
                    ],
                    "validate": [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        }
                    ],
                    "output": [
                        {
                            "name": "write thumbnail",
                            "plugin": "thumbnail"
                        }
                    ]
                },
                "reviewable": {
                    "collect": [
                        {
                            "name": "select camera to playblast",
                            "plugin": "camera",
                            "options": {"camera_name": "persp"}
                        }
                    ],
                    "validate": [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        }
                    ],
                    "output": [
                        {
                            "name": "write reviewable",
                            "plugin": "reviewable"
                        }
                    ]
                }
            },
            "publish":[
                {
                    "name": "to ftrack server",
                    "plugin":"result",
                    "visible":False
                }
            ]
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
        'topic={} and data.pipeline.type=publisher and data.pipeline.host=3dsmax'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
