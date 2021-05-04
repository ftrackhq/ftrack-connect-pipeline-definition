# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import os
from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

class FtrackPublishResultUnrealPlugin(plugin.PublisherFinalizerUnrealPlugin):
    plugin_name = 'result_unreal'

    def run(self, context=None, data=None, options=None):
        return {}

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FtrackPublishResultUnrealPlugin(api_object)
    plugin.register()
