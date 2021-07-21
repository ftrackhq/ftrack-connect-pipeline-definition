# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectCameraMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'camera'

    def fetch(self, context_data=None, data=None, options=None):
        '''Fetch all cameras from the scene'''
        collected_objects = cmds.listCameras(p=True)
        return collected_objects

    def run(self, context_data=None, data=None, options=None):
        '''Return the long name of the camera from the plugin *options*'''
        camera_name = options.get('camera_name', 'persp')
        cameras = cmds.ls(camera_name, l=True)
        return cameras


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectCameraMayaPlugin(api_object)
    plugin.register()
