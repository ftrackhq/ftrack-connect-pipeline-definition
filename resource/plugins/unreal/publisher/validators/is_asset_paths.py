# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

import unreal as ue

class CheckAssetPathsValidatorPlugin(plugin.PublisherValidatorUnrealPlugin):
    plugin_name = 'is_asset_paths'

    def run(self, context_data=None, data=None, options=None):
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])
        if not collected_objects or len(collected_objects) == 0:
            return (False,
                {'message':'No asset paths added'})
        for p in collected_objects:
            if not isinstance(p, str):
                return (False,
                    {'message':'Only string paths can be added'})
            elif not p.startswith('/Game'):
                return (False,
                    {'message':'Invalid content browser path - "{}"'.format(p)})
        # No need to validate selection, only sequences can be added
        return True

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckAssetPathsValidatorPlugin(api_object)
    plugin.register()
