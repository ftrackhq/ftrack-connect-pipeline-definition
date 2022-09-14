# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderImporterPlugin(plugin.LoaderImporterPlugin):
    plugin_name = 'common_default_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Default loader importer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderImporterPlugin(api_object)
    plugin.register()
