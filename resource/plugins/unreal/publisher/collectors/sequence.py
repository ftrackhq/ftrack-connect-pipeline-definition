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
    def get_all_sequences(as_names=True):
        ''' Returns a list of of all sequences names '''
        result = []
        actors = ue.EditorLevelLibrary.get_all_level_actors()
        for actor in actors:
            if actor.static_class() == ue.LevelSequenceActor.static_class():
                seq = actor.load_sequence()
                result.append(seq.get_name() if as_names else seq)
                break
        return result

    def fetch(self, context=None, data=None, options=None):
        ''' Fetch all the sequence actor names in the project '''
        return CollectSequenceUnrealPlugin.get_all_sequences()

    def add(self, context=None, data=None, options=None):
        ''' Return the selected sequence names. '''
        collected_objects = []
        seq_name_sel = None
        #selectedAssets = ue.EditorUtilityLibrary.get_selected_assets()
        #for asset in selectedAssets:
        #    if asset.static_class() == ue.LevelSequence.static_class():
        #        seq_name_sel = asset.get_name()
        #        break
        
        # First, try to pick the selected
        for actor in ue.EditorLevelLibrary.get_selected_level_actors():
            if actor.static_class() == ue.LevelSequenceActor.static_class():
                seq_name_sel = actor.get_name()
                break
        if not seq_name_sel:
            # No one selected, pick the first found
            all_sequences = CollectSequenceUnrealPlugin.get_all_sequences()
            if 0<len(all_sequences):
                seq_name_sel = all_sequences[0]
        collected_objects.append(seq_name_sel)
        return collected_objects

    def run(self, context=None, data=None, options=None):
        '''
        Return the collected objects in the widget from the plugin *options*
        '''
        sequence_objects = options.get('collected_objects', [])
        result = []
        all_sequences = CollectSequenceUnrealPlugin.get_all_sequences(as_names=False)
        for seq_name in sequence_objects:
            for seq in all_sequences:
                if seq.get_name() == seq_name or seq_name.startswith('{}_'.format(seq.get_name())):
                    result.append(seq)
                    break
        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSequenceUnrealPlugin(api_object)
    plugin.register()

