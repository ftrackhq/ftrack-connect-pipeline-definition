# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "Test Comp Publisher",
            "package": "imgPkg",
            "host":"nuke",
            "ui":"qt",
            "context":[
                {
                    "name": "context selector",
                    "plugin": "context.publish",
                    "widget": "context.publish"
                }
            ],
            "components":{
                "nukescript":{
                    "collect":[
                        {
                            "name": "collect scene",
                            "plugin": "nukescene",
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
                            "name": "write nuke script",
                            "plugin": "nukescript"
                        }
                    ]
                },
                "sequence": {
                    "collect": [
                        {
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    "validate": [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        },
                        {
                            "name": "validate node type",
                            "plugin": "node_type",
                            "options": {"node_type": "Write"}
                        }
                    ],
                    "output": [
                        {
                            "name": "write sequence",
                            "plugin": "sequence"
                        }
                    ]
                },
                "thumbnail": {
                    "collect": [
                        {
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    "validate": [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        },
                        {
                            "name": "validate node type",
                            "plugin": "node_type",
                            "options": {"node_type": "Write"}
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
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    "validate": [
                        {
                            "name": "validate selection",
                            "plugin": "nonempty"
                        },
                        {
                            "name": "validate node type",
                            "plugin": "node_type",
                            "options": {"node_type": "Write"}
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
        'topic={} and data.pipeline.type=publisher'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
