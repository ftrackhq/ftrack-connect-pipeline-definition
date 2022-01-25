# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack
import logging

import hou

import ftrack_api
from ftrack_connect_pipeline_houdini import plugin


logger = logging.getLogger('ftrack_connect_pipeline_houdini')


class CheckGeometryValidatorPlugin(plugin.PublisherValidatorHoudiniPlugin):
    plugin_name = 'is_geometry'

    def run(self, context_data=None, data=None, options=None):
        if not data:
            return (False, 'Please add objects for publishing!')
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])
        for obj_path in collected_objects:
            obj = hou.node(obj_path)
            if obj.type().name() != 'geo':
                return (
                    False,
                    {
                        'message': '({}) Only geometry can be published!'.format(
                            obj_path
                        )
                    },
                )
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckGeometryValidatorPlugin(api_object)
    plugin.register()
