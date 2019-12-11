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
            "host":"api",
            "ui":None,
            constants.CONTEXT:[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            constants.COMPONENTS: [
                {
                    "name": "main",
                    "stages": [
                        {constants.COLLECTORS:[
                            {
                                "name": "Pick selected object/s",
                                "plugin":"selection",
                            }
                        ]},
                        {constants.VALIDATORS:[
                            {
                                "name": "validate selection",
                                "plugin":"nonempty"
                            }
                        ],},
                        {constants.OUTPUTS:[
                            {
                                "name": "maya",
                                "plugin": "mayabinary",
                                "options": {
                                    "preserve_reference": False,
                                    "history": False,
                                    "channels": True,
                                    "expressions": False,
                                    "constraints": False,
                                    "shaders": True,
                                    "include_scene_to_assets": False,
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
                                "name": "select camera to playblast",
                                "plugin": "camera",
                                "options": {"camera_name": "persp"}
                            }
                        ],},
                        {constants.VALIDATORS: [
                            {
                                "name": "validate selection",
                                "plugin": "nonempty"
                            }
                        ],},
                        {constants.OUTPUTS: [
                            {
                                "name": "write thumbnail",
                                "plugin": "thumbnail"
                            }
                        ]}
                    ]
                },
                {
                    "name": "reviewable",
                    "stages": [
                        {constants.COLLECTORS: [
                            {
                                "name": "select camera to playblast",
                                "plugin": "camera",
                                "options": {"camera_name": "persp"}
                            }
                        ],},
                        {constants.VALIDATORS: [
                            {
                                "name": "validate selection",
                                "plugin": "nonempty"
                            }
                        ],},
                        {constants.OUTPUTS: [
                            {
                                "name": "write reviewable",
                                "plugin": "reviewable"
                            }
                        ]},
                    ]
                },
            ],
            constants.PUBLISHERS: [
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
        'topic={} and data.pipeline.type=publisher and data.pipeline.host=api'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
