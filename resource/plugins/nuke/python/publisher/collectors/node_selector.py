# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin


class NodeSelectorNukePlugin(plugin.NukePublisherCollectorPlugin):
    plugin_name = 'node_selector'

    def fetch(self, context_data=None, data=None, options=None):
        '''Return a dictionary with all the nodes in nuke and if some are
        selected, the last one is added on last_selected_node'''
        result = {}
        all_nodes = nuke.allNodes()
        node_names = [node.name() for node in all_nodes]
        last_selected_node = None
        if nuke.selectedNodes():
            last_selected_node = nuke.selectedNodes()[0]
        result = {
            'all_nodes': node_names,
            'last_selected_node': last_selected_node.name(),
        }
        return result

    def run(self, context_data=None, data=None, options=None):
        '''Return the node name passed on the plugin *options*'''
        node_name = options['node_name']
        return [node_name]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NodeSelectorNukePlugin(api_object)
    plugin.register()
