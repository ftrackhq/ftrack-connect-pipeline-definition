# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectCameraMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'camera'

    def fetch(self, context=None, data=None, options=None):
        collected_objects = cmds.listCameras(p=True)
        return collected_objects

    def run(self, context=None, data=None, options=None):
        camera_name = options.get('camera_name', 'persp')
        cameras = cmds.ls(camera_name, l=True)
        return cameras


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectCameraMayaPlugin(api_object)
    plugin.register()

