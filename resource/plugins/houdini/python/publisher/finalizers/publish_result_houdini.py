# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import os
from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class FtrackPublishResultHoudiniPlugin(plugin.PublisherFinalizerHoudiniPlugin):
    plugin_name = 'result_houdini'

    def run(self, context_data=None, data=None, options=None):
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FtrackPublishResultHoudiniPlugin(api_object)
    plugin.register()
