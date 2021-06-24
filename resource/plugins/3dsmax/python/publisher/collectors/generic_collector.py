# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
import ftrack_api
from pymxs import runtime as rt


class CollectGenericMaxPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'generic_collector'

    def select(self, context_data=None, data=None, options=None):
        '''Select all the items of the plugin *options*'''
        selected_items = options.get('selected_items', [])
        nodes_to_select = []
        for item in selected_items:
            nodes_to_select.append(rt.getNodeByName(item))
        rt.select(nodes_to_select)
        return rt.selection

    def fetch(self, context_data=None, data=None, options=None):
        '''Fetch all selected items'''
        collected_objects = []
        selected_objects = rt.selection
        for obj in selected_objects:
            collected_objects.append(obj.name)

        return collected_objects

    def add(self, context_data=None, data=None, options=None):
        '''Return the selected items of the scene'''
        selected_objects = rt.selection
        return selected_objects

    def run(self, context_data=None, data=None, options=None):
        collected_objects = options.get('collected_objects', [])
        return collected_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGenericMaxPlugin(api_object)
    plugin.register()

