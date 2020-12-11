# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_maya import plugin

import maya.cmds as cmds
import ftrack_api


class CheckGeometryValidatorPlugin(plugin.PublisherValidatorMayaPlugin):
    plugin_name = 'is_geometry'

    def run(self, context=None, data=None, options=None):
        if not data:
            return False
        for obj in data:
            if not cmds.objectType(obj, isAType='geometryShape'):
                return False
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckGeometryValidatorPlugin(api_object)
    plugin.register()
