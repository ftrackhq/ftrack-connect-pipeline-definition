# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin

from pymxs import runtime as rt
import ftrack_api


class CheckCamerasValidatorPlugin(plugin.PublisherValidatorMaxPlugin):
    plugin_name = 'is_camera'

    def run(self, context=None, data=None, options=None):
        self.logger.debug("data: {}".format(data))

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        for obj in collected_objects:
            node = rt.getNodeByName(obj)
            is_camera = rt.isKindOf(node, rt.Camera)
            if not is_camera:
                return False
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckCamerasValidatorPlugin(api_object)
    plugin.register()
