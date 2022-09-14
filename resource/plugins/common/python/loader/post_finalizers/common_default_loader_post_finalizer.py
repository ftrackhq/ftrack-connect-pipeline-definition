# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderPostFinalizerPlugin(plugin.LoaderPostFinalizerPlugin):
    plugin_name = 'common_default_loader_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Default loader post finalizer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderPostFinalizerPlugin(api_object)
    plugin.register()
