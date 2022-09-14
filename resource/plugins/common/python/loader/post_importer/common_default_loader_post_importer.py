# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderPostImporterPlugin(plugin.LoaderPostImporterPlugin):
    plugin_name = 'common_default_loader_post_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Default loader post importer finalizer plugin'''
        return (
            {},
            {
                'message': 'No Data is imported this is for testing purposes',
                'data': ['abcde'],
            },
        )


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderPostImporterPlugin(api_object)
    plugin.register()
