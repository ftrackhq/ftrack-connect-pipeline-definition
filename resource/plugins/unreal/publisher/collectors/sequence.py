# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import unreal as ue

from ftrack_connect_pipeline_unreal_engine import plugin
import ftrack_api

class CollectSequenceUnrealPlugin(plugin.PublisherCollectorUnrealPlugin):
    plugin_name = 'sequence_collector'

    def select(self, context=None, data=None, options=None):
        '''Select all the sequences in the given plugin *options*'''
        selected_items = options.get('selected_items', [])
        # TODO: Can sequences be selected?
        #for obj in hou.node('/').allSubChildren():
        #    obj.setSelected(1, obj in selected_items or obj.path() in selected_items)
        return selected_items

    @staticmethod
    def get_all_sequences():
        result = []
        actors = ue.EditorLevelLibrary.get_all_level_actors()
        for actor in actors:
            if actor.static_class() == ue.LevelSequenceActor.static_class():
                result.append(actor.load_sequence())
                break
        return result

    def fetch(self, context=None, data=None, options=None):
        ''' Fetch all the sequences in the scene '''
        return CollectSequenceUnrealPlugin.get_all_sequences()

    def add(self, context=None, data=None, options=None):
        ''' Return the selected sequences, verify type. '''
        # Here we return the first available master sequence for now
        # TODO: Can we detect which sequence(s) are selected?
        collected_objects = []
        all_sequences = CollectSequenceUnrealPlugin.get_all_sequences()
        if 0<len(all_sequences):
            collected_objects.append(all_sequences[0])
        return collected_objects

    def run(self, context=None, data=None, options=None):
        '''
        Return the collected objects in the widget from the plugin *options*
        '''
        sequence_objects = options.get('collected_objects', [])
        return sequence_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSequenceUnrealPlugin(api_object)
    plugin.register()

