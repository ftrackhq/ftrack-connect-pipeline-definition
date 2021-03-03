# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_unreal import plugin

import ftrack_api

import unreal as ue

class CheckSequenceValidatorPlugin(plugin.PublisherValidatorUnrealPlugin):
    plugin_name = 'is_sequence'

    def run(self, context=None, data=None, options=None):
        if not data:
            return False
        for actor in data:
            if actor.static_class() != ue.LevelSequenceActor.static_class():
               return False
    return True

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckSequenceValidatorPlugin(api_object)
    plugin.register()
