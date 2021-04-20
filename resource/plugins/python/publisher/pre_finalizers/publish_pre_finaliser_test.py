# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
from ftrack_connect_pipeline import plugin
import ftrack_api

class PublishPreFinalizerTestPlugin(plugin.PublisherPreFinalizerPlugin):
    plugin_name = 'pre_result'

    def run(self, context=None, data=None, options=None):
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = PublishPreFinalizerTestPlugin(api_object)
    plugin.register()
