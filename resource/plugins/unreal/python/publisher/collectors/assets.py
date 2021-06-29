# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import unreal as ue

from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

class CollectAssetsUnrealPlugin(plugin.PublisherCollectorUnrealPlugin):
    plugin_name = 'assets_collector'

    def select(self, context_data=None, data=None, options=None):
        '''Select all the sequences in the given plugin *options*'''
        selected_items = options.get('selected_items', [])
        return selected_items

    def fetch(self, context_data=None, data=None, options=None):
        ''' Fetch all the sequence actor names in the project '''
        collected_objects = []

        unreal_map = ue.EditorLevelLibrary.get_editor_world()
        unreal_map_package_path = unreal_map.get_outermost().get_path_name()

        collected_objects.append(unreal_map_package_path)

        return collected_objects

    def add(self, context_data=None, data=None, options=None):
        ''' Return selected selected content browser packe paths. '''
        # TODO find a way to check what is selected
        return self.fetch(context_data, data, options)

    def run(self, context_data=None, data=None, options=None):
        '''
        Return the collected objects in the widget from the plugin *options*
        '''
        sequence_objects = options.get('collected_objects', [])
        return sequence_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectAssetsUnrealPlugin(api_object)
    plugin.register()

