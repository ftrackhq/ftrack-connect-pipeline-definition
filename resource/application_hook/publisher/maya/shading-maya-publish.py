# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import json


def register_publisher(event):
    # return json so we can validate it
    return json.dumps(
        {
          "name": "Lookdev Publisher",
          "package": "shadPackage",
          "host":"maya",
          "ui":"qt",
          "context":[
              {
                "name": "context selector",
                "plugin": "context.publish",
                "widget": "context.publish"
              }
          ],
          "components": {
            "main": {
              "collect": [
                {
                  "name": "collect from scene",
                  "plugin": "scene"
                }
              ],
              "validate": [
                {
                  "name": "validate selection",
                  "plugin": "non_empty"
                }
              ],
              "output": [
                {
                  "name": "mayascii",
                  "plugin": "geometry",
                  "editable": False,
                  "options": {
                    "file_type": "ma",
                    "animated": False
                  }
                }
              ]
            },
            "reviewable": {
              "collect": [
                {
                  "name": "from scene",
                  "plugin": "scene"
                }
              ],
              "validate": [
                {
                  "name": "validate selection",
                  "plugin": "non_empty"
                }
              ],
              "output": [
                {
                  "name": "playblast",
                  "plugin": "playblast",
                  "options": {
                    "camera": "persp",
                    "start_frame": 0,
                    "end_frame": 100,
                    "file_type": "mov-h264"
                  }
                }
              ]
            },
            "thumbnail": {
              "collect": [
                {
                  "name": "from viewport",
                  "plugin": "from_viewport"
                }
              ],
              "validate": [
                {
                  "name": "validate selection",
                  "plugin": "non_empty"
                }
              ],
              "output": [
                {
                  "name": "thumbnail",
                  "plugin": "image",
                  "options": {
                    "file_type": "jpg"
                  }
                }
              ]
            },
          },
          "publish": [
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
        'topic={} and data.pipeline.type=publisher'.format(constants.PIPELINE_REGISTER_TOPIC),
        register_publisher
    )
