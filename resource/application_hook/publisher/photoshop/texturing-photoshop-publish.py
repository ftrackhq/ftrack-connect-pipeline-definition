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
                    "plugin":"context_selector",
                    "widget":"thumbnails"
                }
            ],
            "components":{
                "color":{
                    "collect":[
                        {
                            "plugin":"from_suffix",
                            "options": {
                                "suffix": "diff_"
                            }
                        }
                    ],
                    "validate":[
                        {
                            "plugin":"non_empty"
                        }
                    ],
                    "output":[
                        {
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                "diffuse":{
                    "collect":[
                        {
                            "plugin":"from_prefix",
                            "options": {
                                "suffix": "diff_"
                            }
                        }
                    ],
                    "validate":[
                        {
                            "plugin":"non_empty"
                        }
                    ],
                    "output":[
                        {
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
               "specular":{
                    "collect":[
                        {
                            "plugin":"from_prefix",
                            "options": {
                                "suffix": "spec_"
                            }
                        }
                    ],
                    "validate":[
                        {
                            "plugin":"non_empty"
                        }
                    ],
                    "output":[
                        {
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                "bump":{
                    "collect":[
                        {
                            "plugin":"from_prefix",
                            "options": {
                                "suffix": "spec_"
                            }
                        }
                    ],
                    "validate":[
                        {
                            "plugin":"non_empty"
                        }
                    ],
                    "output":[
                        {
                            "plugin":"image",
                            "options":{
                                "file_type":"exr",
                                "color_depth": 16
                            }
                        }
                    ]
                },
                "thumbnail": {
                    "collect":[
                        {
                            "plugin":"from_component",
                            "options": {
                                "component": "color"
                            }
                        }
                    ],
                    "validate":[
                        {
                            "plugin":"non_empty"
                        }
                    ],
                    "output":[
                        {
                            "plugin":"image",
                            "options":{
                                "file_type":"jpg"
                            }
                        }
                    ]
                }
            },
            "publish":[
                {
                    "plugin":"to_ftrack",
                    "visible":False
                },
                {
                    "plugin":"metadata",
                    "visible":True
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
        'topic={} and data.pipeline.type=publisher'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )