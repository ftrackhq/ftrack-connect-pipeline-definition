# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Texture Publisher",
            "package": "textPackage",
            "host":"photoshop",
            "ui":"js",
            "context":[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            "components":[
                {
                    "name": "color",
                    constants.COLLECT:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "col_"
                            }
                        }
                    ],
                    constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],
                    constants.OUTPUT:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                {
                    "name": "diffuse",
                      constants.COLLECT:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "diff_"
                            }
                        }
                    ],
                    constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],
                    constants.OUTPUT:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                {
                    "name": "specular",
                    constants.COLLECT:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "spec_"
                            }
                        }
                    ],
                    constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],
                    constants.OUTPUT:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                {
                    "name": "bump",
                      constants.COLLECT:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "bump_"
                            }
                        }
                    ],
                    constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],
                    constants.OUTPUT:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                {
                    "name": "thumbnail",
                    constants.COLLECT: [
                        {
                            "name": "from viewport",
                            "plugin": "from_viewport"
                        }
                    ],
                    constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],
                    constants.OUTPUT: [
                        {
                            "name": "thumbnail",
                            "plugin": "image",
                            "options": {
                                "file_type": "jpg"
                            }
                        }
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
        'topic={} and data.pipeline.type=publisher and data.pipeline.host=photoshop'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )