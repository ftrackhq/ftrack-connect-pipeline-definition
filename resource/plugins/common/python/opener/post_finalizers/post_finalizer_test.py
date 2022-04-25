# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class PostFinalizerOpenerTest(plugin.OpenerPostFinalizerPlugin):
    plugin_name = 'post_finalizer_test'

    def run(self, context_data=None, data=None, options=None):
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = PostFinalizerOpenerTest(api_object)
    plugin.register()
