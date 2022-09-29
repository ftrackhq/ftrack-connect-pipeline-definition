# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonPassthroughLoaderContextPlugin(plugin.LoaderContextPlugin):
    plugin_name = 'common_passthrough_loader_context'
    '''Option passthrough loader context plugin'''

    def run(self, context_data=None, data=None, options=None):
        '''Merge context output with *options*'''
        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonPassthroughLoaderContextPlugin(api_object)
    plugin.register()
