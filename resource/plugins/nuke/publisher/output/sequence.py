# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api
import os
import clique
import tempfile

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils

import nuke


class OutputSequencePlugin(plugin.PublisherOutputNukePlugin):
    plugin_name = 'sequence'

    def run(self, context=None, data=None, options=None):
        node_name = data[0]
        input_node = nuke.toNode(node_name)
        selected_nodes = nuke.selectedNodes()
        nuke_utils.cleanSelection()

        write_node = nuke.createNode('Write')
        write_node.setInput(0, input_node)

        default_file_format = str(options.get('file_format'))
        selected_file_format = str(options.get('image_format'))
        default_file_format_options = options.get('file_format_options')

        # Generate output file name for mov.
        temp_name = tempfile.NamedTemporaryFile()

        first = str(int(write_node['first'].getValue()))
        last = str(int(write_node['last'].getValue()))
        digit_len = int(len(last)+1)

        temp_seq_path = '{}.%0{}d.{}'.format(
            temp_name.name, digit_len, selected_file_format
        )
        sequence_path = clique.parse(
            '{} [{}-{}]'.format(temp_seq_path, first, last)
        )

        write_node['file'].setValue(temp_seq_path)

        write_node['file_type'].setValue(selected_file_format)
        if selected_file_format == default_file_format:
            for k, v in default_file_format_options.items():
                write_node[k].setValue(int(v))

        ranges = nuke.FrameRanges('{}-{}'.format(first, last))
        nuke.render(write_node, ranges)

        component_name = options['component_name']

        #delete temporal write node
        nuke.delete(write_node)
        #restore selection
        nuke_utils.cleanSelection()
        for node in selected_nodes:
            node['selected'].setValue(True)

        return {component_name: str(sequence_path)}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputSequencePlugin(api_object)
    plugin.register()