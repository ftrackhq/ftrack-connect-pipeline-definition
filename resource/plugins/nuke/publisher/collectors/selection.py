# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin


class CollectSelectedNodesNukePlugin(plugin.PublisherCollectorNukePlugin):
    plugin_name = 'selection'

    def run(self, context_data=None, data=None, options=None):

        selected_nodes = nuke.selectedNodes()
        selected_node_names = []
        for node in selected_nodes:
            selected_node_names.append(node.knob('name').value())
        return selected_node_names


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSelectedNodesNukePlugin(api_object)
    plugin.register()

