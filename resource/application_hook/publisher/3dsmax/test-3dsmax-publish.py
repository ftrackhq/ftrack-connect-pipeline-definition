# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json

from ftrack_connect_pipeline import constants
import ftrack_api


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Geometry Publisher",
            "package": "geoPkg",
            "host": "3dsmax",
            "ui": "qt",
            "context": [
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            "components": [
                {
                    "name": "main",
                    "stages": [
                    {constants.COLLECT: [
                        {
                            "name": "Pick selected object/s",
                            "plugin": "selection",
                        }
                    ],},
                    {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        }
                    ],},
                    {constants.OUTPUT: [
                        {
                            "name": "3dsmaxalembic",
                            "plugin": "OutputMaxAlembicPlugin"
                        }
                    ]},
                    ]
                },
                {
                    "name": "thumbnail",
                    "stages": [
                    {constants.COLLECT: [
                        {
                            "name": "select viewport to playblast",
                            "plugin": "viewport",
                            "widget": "viewport",
                        }
                    ],},
                    {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        }
                    ],},
                    {constants.OUTPUT: [
                        {
                            "name": "write thumbnail",
                            "plugin": "thumbnail"
                        }
                    ]},
                    ]
                },
                {
                    "name": "reviewable",
                    "stages": [
                    {constants.COLLECT: [
                        {
                            "name": "select viewport to playblast",
                            "plugin": "viewport",
                            "widget": "viewport",
                        }
                    ],},
                    {constants.VALIDATE: [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        }
                    ],},
                    {constants.OUTPUT: [
                        {
                            "name": "write reviewable",
                            "plugin": "reviewable"
                        }
                    ]},
                    ]
                }
            ],
            constants.PUBLISH: [
                {
                    "name": "to ftrack server",
                    "plugin": "result",
                    "visible": False
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
        'topic={}'
        ' and data.pipeline.type=publisher'
        ' and data.pipeline.host=3dsmax'.format(
            constants.PIPELINE_REGISTER_TOPIC
        ),
        register_publisher
    )
