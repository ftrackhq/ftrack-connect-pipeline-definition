# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
import ftrack_api


class CollectGeometryMayaPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'geometry_collector'

    def run(self, context=None, data=None, options=None):
        geo_objects = options.get('collected_objects', [])
        # geo_objects = cmds.ls(geometry=True)
        return geo_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGeometryMayaPlugin(api_object)
    plugin.register()

