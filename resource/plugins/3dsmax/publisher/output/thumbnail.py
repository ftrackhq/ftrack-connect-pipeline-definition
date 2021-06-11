# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import os
import uuid

from pymxs import runtime as rt

from ftrack_connect_pipeline_3dsmax import plugin


class OutputThumbnailPlugin(plugin.PublisherOutputMaxPlugin):
    plugin_name = 'thumbnail'

    def run(self, context_data=None, data=None, options=None):
        component_name = options['component_name']
        bm = rt.viewport.getViewportDib(index=rt.viewport.activeViewport)
        #rt.getBitmapInfo(bm)
        filename = '{0}.jpg'.format(uuid.uuid4().hex)
        outpath = os.path.join(rt.pathConfig.GetDir(rt.name("temp")), filename)
        bm.filename = outpath
        rt.save(bm)
        return [outpath]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputThumbnailPlugin(api_object)
    plugin.register()
