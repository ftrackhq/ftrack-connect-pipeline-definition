# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectCameraMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'selection'

    def run(self, context_data=None, data=None, options=None):
        selection = cmds.ls(sl=True)
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectCameraMayaPlugin(api_object)
    plugin.register()
