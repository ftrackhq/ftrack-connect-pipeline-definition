# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderFinalizerPlugin(plugin.LoaderFinalizerPlugin):
    plugin_name = 'common_default_loader_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Default loader finalizer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderFinalizerPlugin(api_object)
    plugin.register()
