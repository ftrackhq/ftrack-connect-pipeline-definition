# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import plugin


class DiscoverAssetsPlugin(plugin.AssetManagerDiscoverPlugin):
    plugin_name = 'filter_assets'

    def run(self, context_data=None, data=None, options=None):
        # TODO: this is just an example
        filter = {'asset_name': 'torso', 'asset_type_name': 'geo'}

        return filter


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = DiscoverAssetsPlugin(api_object)
    plugin.register()
