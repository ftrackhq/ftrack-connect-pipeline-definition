# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from ftrack_connect_pipeline_3dsmax import plugin
from pymxs import runtime as rt


class CollectViewportMaxPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'viewport'

    def fetch(self, context_data=None, data=None, options=None):
        viewports = []
        for idx in range(1, (rt.viewport.numViewEx() + 1)):
            view_type = rt.viewport.getType(index=idx)
            entry = (str(view_type), idx)
            if str(view_type) == 'view_persp_user':  # USER_PERSP
                viewports.insert(0, entry)
            else:
                viewports.append(entry)
        return viewports

    def run(self, context_data=None, data=None, options=None):
        viewport_index = options.get('viewport_index', -1)
        if viewport_index != -1:
            return [viewport_index]
        return []


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectViewportMaxPlugin(api_object)
    plugin.register()
