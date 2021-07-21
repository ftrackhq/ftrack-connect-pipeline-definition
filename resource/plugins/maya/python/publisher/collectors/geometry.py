# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectGeometryMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'geometry_collector'

    def select(self, context_data=None, data=None, options=None):
        '''Select all the items in the given plugin *options*'''
        selected_items = options.get('selected_items', [])
        cmds.select(cl=True)
        for item in selected_items:
            cmds.select(item, add=True)
        return selected_items

    def fetch(self, context_data=None, data=None, options=None):
        '''Fetch all the geometries in the scene'''
        collected_objects = cmds.ls(geometry=True, l=True)
        return collected_objects

    def add(self, context_data=None, data=None, options=None):
        '''Return the selected geometries'''
        check_type = "geometryShape"
        selected_objects = cmds.ls(sl=True, l=True)
        collected_objects = []
        for obj in selected_objects:
            if not cmds.objectType(obj, isAType=check_type):
                relatives = cmds.listRelatives(obj, f=True)
                for relative in relatives:
                    if cmds.objectType(relative, isAType=check_type):
                        collected_objects.append(relative)
            else:
                collected_objects.append(obj)
        return collected_objects

    def run(self, context_data=None, data=None, options=None):
        '''
        Return the collected objects in the widget from the plugin *options*
        '''
        geo_objects = options.get('collected_objects', [])
        return geo_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGeometryMayaPlugin(api_object)
    plugin.register()
