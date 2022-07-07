# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderContextPlugin(plugin.LoaderContextPlugin):
    plugin_name = 'common_default_loader_context'

    def run(self, context_data=None, data=None, options=None):
        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderContextPlugin(api_object)
    plugin.register()