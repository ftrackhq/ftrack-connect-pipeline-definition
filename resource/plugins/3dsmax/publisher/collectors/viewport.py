# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from ftrack_connect_pipeline_3dsmax import plugin
import MaxPlus


class CollectViewportMaxPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'viewport'

    def fetch(self, context=None, data=None, options=None):
        viewports = []
        for index, view in enumerate(MaxPlus.ViewportManager.Viewports):
            entry = (MaxPlus.ViewportManager.getViewportLabel(index), index)
            view_type = view.GetViewType()
            if view_type == 7:  # USER_PERSP
                viewports.insert(0, entry)
            else:
                viewports.append(entry)
        return viewports

    def run(self, context=None, data=None, options=None):
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
