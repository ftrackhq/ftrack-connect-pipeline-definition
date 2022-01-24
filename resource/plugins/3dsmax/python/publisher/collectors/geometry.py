# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
import ftrack_api
from pymxs import runtime as rt


class CollectGeometryMayaPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'geometry_collector'

    def select(self, context_data=None, data=None, options=None):
        '''Select all the items in the given plugin *options*'''
        selected_items = options.get('selected_items', [])
        nodes_to_select = []
        for item in selected_items:
            nodes_to_select.append(rt.getNodeByName(item))
        rt.select(nodes_to_select)
        return rt.selection

    def fetch(self, context_data=None, data=None, options=None):
        '''Fetch all the geometries in the scene'''
        collected_objects = []
        all_objects = rt.objects
        for obj in all_objects:
            if rt.superClassOf(obj) == rt.GeometryClass:
                collected_objects.append(obj.name)

        return collected_objects

    def add(self, context_data=None, data=None, options=None):
        '''Return the selected geometries'''
        selected_objects = rt.selection
        check_type = rt.GeometryClass
        collected_objects = []
        for obj in selected_objects:
            if rt.superClassOf(obj) == check_type:
                collected_objects.append(obj.name)
        return collected_objects

    def run(self, context_data=None, data=None, options=None):
        geo_objects = options.get('collected_objects', [])
        # geo_objects = cmds.ls(geometry=True)
        return geo_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGeometryMayaPlugin(api_object)
    plugin.register()
