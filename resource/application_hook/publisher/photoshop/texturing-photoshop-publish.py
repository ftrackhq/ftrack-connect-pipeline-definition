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
            constants.CONTEXT:[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            constants.COMPONENTS:[
                {
                    "name": "color",
                    "stages": [
                        {constants.COLLECTORS:[
                            {
                                "name": "collect from layer",
                                "plugin":"from_layer",
                                "options": {
                                    "prefix": "col_"
                                }
                            }
                        ],},
                        {constants.VALIDATORS:[
                            {
                                "name": "validate selection",
                                "plugin":"non_empty"
                            }
                        ],},
                        {constants.OUTPUTS:[
                            {
                                "name": "texture layer",
                                "plugin":"image",
                                "options":{
                                    "file_type":"exr",
                                    "color_depth": 16
                                }
                            }
                        ]},
                        ]
                },
                {
                    "name": "diffuse",
                    "stages": [
                        {constants.COLLECTORS:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "diff_"
                            }
                        }
                        ],},
                        {constants.VALIDATORS:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                        ],},
                        {constants.OUTPUTS:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                        ]},
                    ]
                },
                {
                    "name": "specular",
                    "stages": [
                        {constants.COLLECTORS:[
                            {
                                "name": "collect from layer",
                                "plugin":"from_layer",
                                "options": {
                                    "prefix": "spec_"
                                }
                            }
                        ],},
                        {constants.VALIDATORS:[
                            {
                                "name": "validate selection",
                                "plugin":"non_empty"
                            }
                        ],},
                        {constants.OUTPUTS:[
                            {
                                "name": "texture layer",
                                "plugin":"image",
                                "options":{
                                    "file_type":"exr",
                                    "color_depth": 16
                                }
                            }
                        ]},
                    ]
                },
                {
                    "name": "bump",
                    "stages": [
                        {constants.COLLECTORS:[
                        {
                            "name": "collect from layer",
                            "plugin":"from_layer",
                            "options": {
                                "prefix": "bump_"
                            }
                        }
                    ],},
                        {constants.VALIDATORS:[
                        {
                            "name": "validate selection",
                            "plugin":"non_empty"
                        }
                    ],},
                        {constants.OUTPUTS:[
                        {
                            "name": "texture layer",
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]},
                ]
                },
                {
                    "name": "thumbnail",
                    "stages": [
                        {constants.COLLECTORS: [
                        {
                            "name": "from viewport",
                            "plugin": "from_viewport"
                        }
                    ],},
                        {constants.VALIDATORS: [
                        {
                            "name": "validate selection",
                            "plugin": "non_empty"
                        }
                    ],},
                        {constants.OUTPUTS: [
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
            constants.PUBLISHERS:[
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