# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api

class CollectGeometryHoudiniPlugin(plugin.PublisherCollectorHoudiniPlugin):
    plugin_name = 'geometry_collector'

    def select(self, context=None, data=None, options=None):
        '''Select all the items in the given plugin *options*'''
        self.logger.info('@@@ CollectGeometryHoudiniPlugin::select({},{},{})'.format(context, data, options))
        selected_items = options.get('selected_items', [])
        for obj in hou.node('/').allSubChildren():
            obj.setSelected(1, obj in selected_items or obj.path() in selected_items)
        return selected_items

    def fetch(self, context=None, data=None, options=None):
        '''Fetch all the geometries in the scene'''
        self.logger.info('@@@ CollectGeometryHoudiniPlugin::fetch({},{},{})'.format(context, data, options))
        collected_objects = hou.node('/').allSubChildren()
        return [obj.path() for obj in collected_objects]

    def add(self, context=None, data=None, options=None):
        '''Return the selected geometries'''
        self.logger.info('@@@ CollectGeometryHoudiniPlugin::add({},{},{})'.format(context, data, options))
        check_type = "geometryShape"
        selected_objects = hou.selectedNodes()
        objPath = hou.node('/obj')
        geometry_objects = objPath.glob('*')
        collected_objects = []
        for obj in selected_objects:
            if obj in geometry_objects:
                collected_objects.append(obj.path())
        return collected_objects

    def run(self, context=None, data=None, options=None):
        '''
        Return the collected objects in the widget from the plugin *options*
        '''
        geo_objects = options.get('collected_objects', [])
        self.logger.info('@@@ CollectGeometryHoudiniPlugin::run({},{},{}), geo_objects: {}'.format(context, data, options, geo_objects))
        return geo_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectGeometryHoudiniPlugin(api_object)
    plugin.register()

