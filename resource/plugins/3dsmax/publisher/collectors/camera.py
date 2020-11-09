# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from pymxs import runtime as rt

from ftrack_connect_pipeline_3dsmax import plugin


class CollectCameraMaxPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'camera'
    MAX_CAMERA_CLASS_ID = 32

    def fetch(self, context=None, data=None, options=None):
        '''Fetch all cameras from the scene'''
        cameras = []
        for obj in rt.rootScene.world.children:
            if rt.SuperClassOf(obj) == rt.camera:
                cameras.append(obj.name)
        return cameras

    def run(self, context=None, data=None, options=None):
        self.logger.debug("camera Run options: {}".format(options))
        camera_name = options.get('camera_name', 'persp')
        camera = rt.getNodeByName(camera_name)
        if camera:
            return [camera.name]
        return []


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectCameraMaxPlugin(api_object)
    plugin.register()
