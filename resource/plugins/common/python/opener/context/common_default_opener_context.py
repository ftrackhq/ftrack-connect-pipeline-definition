# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultOpenerContextPlugin(plugin.OpenerContextPlugin):
    plugin_name = 'common_default_opener_context'

    def run(self, context_data=None, data=None, options=None):
        '''Default opener context plugin'''
        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultOpenerContextPlugin(api_object)
    plugin.register()
