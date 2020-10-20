# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectGenericMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'generic_collector'

    def fetch(self, context=None, data=None, options=None):
        # selected_objects = cmds.ls(sl=True, l=True)
        # check_type = "geometryShape"
        # current_objects = self.get_current_objects()
        # for obj in selected_objects:
        #     if not cmds.objectType(obj, isAType=check_type):
        #         relatives = cmds.listRelatives(obj, f=True)
        #         for relative in relatives:
        #             if cmds.objectType(relative, isAType=check_type):
        #                 obj = relative
        #     if obj in current_objects:
        #         continue
        #     self.add_object(obj)

        collected_objects = cmds.ls(sl=True, l=True)
        return collected_objects

    def run(self, context=None, data=None, options=None):
        collected_objects = options.get('collected_objects', [])
        return collected_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGenericMayaPlugin(api_object)
    plugin.register()

