# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Comp Publisher",
            "package": "compPackage",
            "host":"nuke",
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
                    "name": "script",
                    "stages": [
                        {constants.COLLECT:[
                        {
                            "name": "from scene",
                            "plugin":"from_scene",
                            "options": {
                              "node_type": "write"
                            }
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
                            "name": "nuke file",
                            "plugin":"nuke_file",
                            "editable":False,
                            "options":{
                                "file_type":"nk"
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
                            "name": "from nodes",
                            "plugin":"from_nodes",
                            "options": {
                              "node_type": "geo"
                            }
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
                            "name": "alembic",
                            "plugin":"geometry",
                            "editable":False,
                            "options":{
                                "file_type":"abc"
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "beauty",
                    "stages": [
                        {constants.COLLECT: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "suffix": "beauty_"
                            }
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "render pass",
                            "plugin": "image",
                            "options": {
                                "file_type": "exr",
                                "color_depth": 16
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "diffuse",
                    "stages": [
                        {constants.COLLECT: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "diff_"
                            }
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "render pass",
                            "plugin": "image",
                            "options": {
                                "file_type": "exr",
                                "color_depth": 16
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "reflection",
                    "stages": [
                        {constants.COLLECT: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "ref_"
                            }
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "render pass",
                            "plugin": "image",
                            "options": {
                                "file_type": "exr",
                                "color_depth": 16
                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "shadow",
                    "stages": [
                        {constants.COLLECT: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "shad_"
                            }
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "render pass",
                            "plugin": "image",
                            "options": {
                                "file_type": "exr",
                                "color_depth": 16
                            }
                        }
                        ]},
                    ]
                },
                {
                    "name": "specular",
                    "stages": [
                        {constants.COLLECT: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "spec_"
                            }
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "render pass",
                            "plugin": "image",
                            "options": {
                                "file_type": "exr",
                                "color_depth": 16
                            }
                        }
                    ]}
                    ]
                },
                {
                    "name": "reviewable",
                    "stages": [
                        {constants.COLLECT:[
                        {
                            "name": "from scene",
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
                        {constants.COLLECT: [
                        {
                            "name": "from viewport",
                            "plugin": "from_viewport"
                        }
                    ],},
                        {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUT: [
                        {
                            "name": "thumbnail",
                            "plugin": "image",
                            "options": {
                                "file_type": "jpg"
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
        'topic={} and data.pipeline.type=publisher and data.pipeline.host=nuke'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
