# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultOpenerPostImportPlugin(plugin.OpenerPostImportPlugin):
    plugin_name = 'common_default_opener_post_import'

    def run(self, context_data=None, data=None, options=None):
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
    plugin = CommonDefaultOpenerPostImportPlugin(api_object)
    plugin.register()
