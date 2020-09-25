# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
import ftrack_api


class CollectGenericMayaPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'generic_collector'

    def run(self, context=None, data=None, options=None):
        collected_objects = options.get('collected_objects', [])
        return collected_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGenericMayaPlugin(api_object)
    plugin.register()

