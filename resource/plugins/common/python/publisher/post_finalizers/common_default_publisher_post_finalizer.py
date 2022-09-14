# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os
from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultPublisherPostFinalizerPlugin(
    plugin.PublisherPostFinalizerPlugin
):
    plugin_name = 'common_default_publisher_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Default publisher post finalizer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultPublisherPostFinalizerPlugin(api_object)
    plugin.register()
