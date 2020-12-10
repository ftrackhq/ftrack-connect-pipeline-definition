# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import hou

from ftrack_connect_pipeline_houdini import plugin

import ftrack_api


class CheckCameraValidatorPlugin(plugin.PublisherValidatorHoudiniPlugin):
    plugin_name = 'is_camera'

    def run(self, context=None, data=None, options=None):
        for obj_path in data:
            obj = hou.node(obj_path)
            if not 'cam' in obj.type().name():
                return False
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckCameraValidatorPlugin(api_object)
    plugin.register()
