# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os
from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class MayaDefaultPublisherFinalizerPlugin(plugin.MayaPublisherFinalizerPlugin):
    plugin_name = 'maya_default_publisher_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Maya publisher finalizer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaDefaultPublisherFinalizerPlugin(api_object)
    plugin.register()
