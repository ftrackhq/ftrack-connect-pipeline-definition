# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class PostImportLoaderTest(plugin.LoaderPostImportPlugin):
    plugin_name = 'post_import_test'

    def run(self, context_data=None, data=None, options=None):
        return (
            {},
            {
                'message': 'No Data is imported this is for testing propouses',
                'data': ['abcde'],
            },
        )


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = PostImportLoaderTest(api_object)
    plugin.register()
