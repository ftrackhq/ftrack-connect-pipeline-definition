# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api
import os

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils

import nuke

class WritableNodeValidatorPlugin(plugin.PublisherValidatorNukePlugin):
    plugin_name = 'can_connect_to_write_node'

    def run(self, context=None, data=None, options=None):
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if len(collected_objects) == 0:
            self.logger.error(
                "No write nodes selected!"
            )
            return (False, {'message':'No write nodes selected!'})
        scene_node = nuke.toNode(collected_objects[0])
        selected_nodes = nuke.selectedNodes()
        nuke_utils.cleanSelection()

        write_node = nuke.createNode('Write')
        if not write_node.setInput(0, scene_node):
            self.logger.error(
                "The selected node can't be connected to a write node"
            )
            return (False, {'message':"The selected node can't be connected to a write node"})
        # delete temporal write node
        nuke.delete(write_node)
        # restore selection
        nuke_utils.cleanSelection()
        for node in selected_nodes:
            node['selected'].setValue(True)
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = WritableNodeValidatorPlugin(api_object)
    plugin.register()
