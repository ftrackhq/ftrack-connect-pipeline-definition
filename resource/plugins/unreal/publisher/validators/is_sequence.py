# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

import unreal as ue

class CheckSequenceValidatorPlugin(plugin.PublisherValidatorUnrealPlugin):
    plugin_name = 'is_sequence'

    def run(self, context=None, data=None, options=None):
        if not data or len(data) == 0:
            return (False, 'No level sequence added!')
        if len(data) != 1:
            return (False, 'More than one(1) level sequence added!')
        # No need to validate selection, only sequences can be added
        return True

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckSequenceValidatorPlugin(api_object)
    plugin.register()
