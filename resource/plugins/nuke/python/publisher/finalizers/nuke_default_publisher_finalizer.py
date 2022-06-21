# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import os
from ftrack_connect_pipeline_nuke import plugin


class NukeDefaultPublisherFinalizerPlugin(plugin.NukePublisherFinalizerPlugin):
    plugin_name = 'nuke_default_publisher_finalizer'

    def run(self, context_data=None, data=None, options=None):
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeDefaultPublisherFinalizerPlugin(api_object)
    plugin.register()
