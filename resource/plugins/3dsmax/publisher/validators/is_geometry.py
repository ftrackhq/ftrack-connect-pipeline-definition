# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin

from pymxs import runtime as rt
import ftrack_api


class CheckCamerasValidatorPlugin(plugin.PublisherValidatorMaxPlugin):
    plugin_name = 'is_geometry'

    def run(self, context=None, data=None, options=None):
        for obj in data:
            node = rt.getNodeByName(obj)
            is_geometry = rt.superClassOf(node, rt.GeometryClass)
            if not is_geometry:
                return False
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckCamerasValidatorPlugin(api_object)
    plugin.register()
