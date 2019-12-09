# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_loader(event):
    # return json so we can validate it
    return json.dumps(
        {
            "name":"CompositingOpen",
            "host":"nuke",
            "ui":"qt",
            constants.COMPONENTS: [
                {
                  "name": "import render layers",
                  "plugin": "images",
                  "options":{
                    "type": "lightPackage",
                    "component": ["beauty", "diffuse", "specular", "reflection", "shadow"]
                  }
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
        'topic={} and data.pipeline.type=loader'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_loader
    )
