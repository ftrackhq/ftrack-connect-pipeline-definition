# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectGenericMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'generic_collector'

    def select(self, context=None, data=None, options=None):
        selected_items = options.get('selected_items', [])
        cmds.select(cl=True)
        for item in selected_items:
            cmds.select(item, add=True)
        return selected_items

    def fetch(self, context=None, data=None, options=None):
        collected_objects = cmds.ls(sl=True, l=True)
        return collected_objects

    def add(self, context=None, data=None, options=None):
        selected_objects = cmds.ls(sl=True, l=True)
        return selected_objects

    def run(self, context=None, data=None, options=None):
        collected_objects = options.get('collected_objects', [])
        return collected_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGenericMayaPlugin(api_object)
    plugin.register()

