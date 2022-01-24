# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
from ftrack_connect_pipeline import plugin
import ftrack_api


class PublishPostFinalizerTestPlugin(plugin.PublisherPostFinalizerPlugin):
    plugin_name = 'post_result'

    def run(self, context_data=None, data=None, options=None):
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = PublishPostFinalizerTestPlugin(api_object)
    plugin.register()
