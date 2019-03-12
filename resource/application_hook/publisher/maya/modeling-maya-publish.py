# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Model Publisher",
            "asset": "modelPackage",
            "host":"maya",
            "ui":"qt",
            "context":[
                {
                    "plugin":"context_selector",
                    "widget":"thumbnails"
                }
            ],
            "components": {
                "main": {
                    "collect": [
                        {
                            "plugin": "scene"
                        }
                    ],
                    "validate": [
                        {
                            "plugin": "non_empty"
                        }
                    ],
                    "output": [
                        {
                            "plugin": "geometry",
                            "editable": False,
                            "options": {
                                "file_type": "ma",
                                "animated": False
                            }
                        }
                    ]
                },
                "cache": {
                    "collect": [
                        {
                            "plugin": "from_set",
                            "editable": False,
                            "options": {
                                "file_type": "mayaascii"
                            }
                        }
                    ],
                    "validate": [
                        {
                            "plugin": "non_empty"
                        },
                        {
                            "plugin": "non_mainfold",
                            "editable": False
                        }
                    ],
                    "output": [
                        {
                            "plugin": "geometry",
                            "editable": False,
                            "options": {
                                "file_type": "alembic"
                            }
                        }
                    ]
                },
                "reviewable": {
                    "collect": [
                        {
                            "plugin": "scene"
                        }
                    ],
                    "validate": [
                        {
                            "plugin": "non_empty"
                        }
                    ],
                    "output": [
                        {
                            "plugin": "playblast",
                            "options": {
                                "start_frame": 0,
                                "end_frame": 100,
                                "file_type": "mov-h264"
                            }
                        }
                    ]
                },
                "thumbnail": {
                    "collect": [
                        {
                            "plugin": "from_viewport"
                        }
                    ],
                    "validate": [
                        {
                            "plugin": "non_empty"
                        }
                    ],
                    "output": [
                        {
                            "plugin": "image",
                            "options": {
                                "file_type": "jpg"
                            }
                        }
                    ]
                },
                "publish": [
                    {
                        "plugin": "to_ftrack",
                        "visible": False
                    },
                    {
                        "plugin": "metadata",
                        "visible": True
                    }
                ]
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
        'topic={} and data.pipeline.type=publisher'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )