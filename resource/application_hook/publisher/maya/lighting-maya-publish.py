# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Lighting Publisher",
            "package": "lightPackage",
            "host":"maya",
            "ui":"qt",
            constants.CONTEXT:[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            constants.COMPONENTS:[
                {
                    "name": "main",
                    "stages": [
                    {constants.COLLECTORS:[
                        {
                            "name": "collect from set",
                            "plugin":"from_set",
                            "options": {
                              "set_name": "GEO"
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
                            "name": "maya ascii",
                            "plugin":"geometry",
                            "editable":False,
                            "options":{
                                "file_type":"ma",
                                "animated":False

                            }
                        }
                    ]},
                    ]
                },
                {
                    "name": "beauty",
                    "stages": [
                    {constants.COLLECTORS: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "beauty_"
                            }
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
                    {constants.COLLECTORS: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "diff_"
                            }
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
                    {constants.COLLECTORS: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "refl_"
                            }
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
                    {constants.COLLECTORS: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "shad_"
                            }
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
                    {constants.COLLECTORS: [
                        {
                            "name": "from prefix",
                            "plugin": "from_prefix",
                            "options": {
                                "prefix": "spec_"
                            }
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
                    "name": "reviewable",
                    "stages": [
                    {constants.COLLECTORS:[
                        {
                            "name": "from scene",
                            "plugin":"scene"
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
                    {constants.COLLECTORS:[
                        {
                            "name": "from viewport",
                            "plugin":"from_viewport"
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
        'topic={} and data.pipeline.type=publisher  and data.pipeline.host=maya'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
