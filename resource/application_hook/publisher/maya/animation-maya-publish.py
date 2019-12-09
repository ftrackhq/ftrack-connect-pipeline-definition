# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Animation Publisher",
            "package": "animPackage",
            "host":"maya",
            "ui":"qt",
            "context":[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            "components":[
                {
                    "name": "main",
                    "stages": [
                    {constants.COLLECT:[
                        {
                            "name": "collect from scene",
                            "plugin":"scene"
                        }
                    ],},
                    {constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],},
                    {constants.OUTPUT:[
                        {
                            "name": "maya ascii",
                            "plugin":"geometry",
                            "editable":False,
                            "options":{
                                "file_type":"ma",
                                "animated":True,
                                "start_frame":0,
                                "end_frame":100
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "cache",
                    "stages": [
                    {constants.COLLECT:[
                        {
                            "name": "collect from set",
                            "plugin":"from_set",
                            "editable":False,
                            "options":{
                                "set_name":"BAKE"
                            }
                        }
                    ],},
                    {constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        },
                        {
                            "name": "ensure mainfold",
                            "plugin":"non_mainfold",
                            "editable":False
                        }
                    ],},
                    {constants.OUTPUT:[
                        {
                            "name": "alembic",
                            "plugin":"geometry",
                            "editable":False,
                            "options":{
                                "file_type":"alembic",
                                "animated":True,
                                "start_frame":0,
                                "end_frame":100
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "reviewable",
                    "stages": [
                    {constants.COLLECT:[
                        {
                            "name": "collect from scene",
                            "plugin":"scene"
                        }
                    ],},
                    {constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],},
                    {constants.OUTPUT:[
                        {
                            "name": "playblast",
                            "plugin":"playblast",
                            "options":{
                                "from_camera": "persp",
                                "start_frame":0,
                                "end_frame":100,
                                "encoding":"h264",
                                "file_type": "mov"
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "thumbnail",
                    "stages": [
                    {constants.COLLECT:[
                        {
                            "name": "from viewport",
                            "plugin":"from_viewport"
                        }
                    ],},
                    {constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],},
                    {constants.OUTPUT:[
                        {
                            "name": "thumbnail",
                            "plugin":"image",
                            "options":{
                                "file_type":"jpg"
                            }
                        }
                    ]},
                    ]
                }
            ],
            constants.PUBLISH:[
                {
                    "name": "to ftrack server",
                    "plugin":"to_ftrack",
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
        'topic={} and data.pipeline.type=publisher  and data.pipeline.host=maya'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
