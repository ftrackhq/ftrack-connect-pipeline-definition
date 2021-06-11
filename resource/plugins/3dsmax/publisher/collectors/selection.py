# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from pymxs import runtime as rt

from ftrack_connect_pipeline_3dsmax import plugin


class CollectSelectionMaxPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'selection'

    def run(self, context_data=None, data=None, options=None):
        selection = [node.getmxsprop('name') for node in rt.selection]
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSelectionMaxPlugin(api_object)
    plugin.register()
