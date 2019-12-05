# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name": "ImageSequence Publisher",
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
            "components":[
                {
                    "name": "nukescript",
                    constants.COLLECT:[
                        {
                            "name": "collect scene",
                            "plugin": "nukescene",
                        }
                    ],
                    constants.VALIDATE:[
                        {
                            "name": "validate selection",
                            "plugin":"nonempty"
                        }
                    ],
                    constants.OUTPUT:[
                        {
                            "name": "write nuke script",
                            "plugin": "nukescript"
                        }
                    ]
                },
                {
                    "name": "sequence",
                    constants.COLLECT: [
                        {
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    constants.VALIDATE: [
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
                    constants.OUTPUT: [
                        {
                            "name": "write sequence",
                            "plugin": "sequence"
                        }
                    ]
                },
                {
                    "name": "thumbnail",
                    constants.COLLECT: [
                        {
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    constants.VALIDATE: [
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
                    constants.OUTPUT: [
                        {
                            "name": "write thumbnail",
                            "plugin": "thumbnail"
                        }
                    ]
                },
                {
                    "name": "reviewable",
                    constants.COLLECT: [
                        {
                            "name": "collect write node.",
                            "plugin": "write_node",
                            "widget": "write_node"
                        }
                    ],
                    constants.VALIDATE: [
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
                    constants.OUTPUT: [
                        {
                            "name": "write reviewable",
                            "plugin": "reviewable"
                        }
                    ]
                }
            ],
            constants.PUBLISH:[
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
        'topic={} and data.pipeline.type=publisher and data.pipeline.host=nuke'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
