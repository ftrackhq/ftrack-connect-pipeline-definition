# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import tempfile
import nuke

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils


class OutputThumbnailPlugin(plugin.PublisherOutputNukePlugin):
    plugin_name = 'thumbnail'

    def run(self, context=None, data=None, options=None):
        node_name = data[0]
        input_node = nuke.toNode(node_name)
        selected_nodes = nuke.selectedNodes()
        nuke_utils.cleanSelection()

        write_node = nuke.createNode('Write')
        write_node.setInput(0, input_node)

        # create reformat ftrack_object
        reformat_node = nuke.nodes.Reformat()
        reformat_node['type'].setValue("to box")
        reformat_node['box_width'].setValue(200.0)

        # connect given write ftrack_object to reformat.
        reformat_node.setInput(0, write_node)

        # create new write for reformat and connect it.
        new_write_node = nuke.nodes.Write()
        new_write_node.setInput(0, reformat_node)

        file_name = tempfile.NamedTemporaryFile(
            delete=False, suffix='.png'
        ).name

        new_write_node['file'].setValue(file_name)
        new_write_node['file_type'].setValue('png')
        # render thumbnail
        curFrame = int(nuke.knob("frame"))

        nuke.execute(new_write_node, curFrame, curFrame)

        # delete thumbnail network after render
        nuke.delete(reformat_node)
        nuke.delete(new_write_node)

        # delete temporal write node
        nuke.delete(write_node)
        # restore selection
        nuke_utils.cleanSelection()
        for node in selected_nodes:
            node['selected'].setValue(True)

        component_name = options['component_name']
        return {component_name: file_name}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputThumbnailPlugin(api_object)
    plugin.register()
