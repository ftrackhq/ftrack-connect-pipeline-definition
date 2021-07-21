# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import tempfile
import nuke

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils


class OutputReviewablePlugin(plugin.PublisherOutputNukePlugin):
    plugin_name = 'reviewable'

    def run(self, context_data=None, data=None, options=None):
        has_to_clean = False

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        node_name = collected_objects[0]
        input_node = nuke.toNode(node_name)
        selected_nodes = nuke.selectedNodes()
        nuke_utils.cleanSelection()

        if input_node.Class() == 'Write':
            write_node = input_node
        else:
            has_to_clean = True
            write_node = nuke.createNode('Write')
            write_node.setInput(0, input_node)


        # node_name = data[0]
        # write_node = nuke.toNode(node_name)

        # Get the input of the given write ftrack_object.
        w_input_node = write_node.input(0)

        # Generate output file name for mov.
        temp_review_mov = tempfile.NamedTemporaryFile(
            delete=False, suffix='.mov'
        ).name

        first = str(int(nuke.root().knob('first_frame').value()))
        last = str(int(nuke.root().knob('last_frame').value()))

        # Create a new write_node.
        review_node = nuke.createNode('Write')
        review_node.setInput(0, w_input_node)
        review_node['file'].setValue(temp_review_mov.replace('\\','/'))
        review_node['file_type'].setValue('mov')
        review_node['mov64_codec'].setValue('png')

        if write_node['use_limit'].getValue():
            review_node['use_limit'].setValue(True)

            first = str(int(write_node['first'].getValue()))
            last = str(int(write_node['last'].getValue()))

            review_node['first'].setValue(int(first))
            review_node['last'].setValue(int(last))

        self.logger.debug('Rendering sequence {}-{}'.format(first, last))
        ranges = nuke.FrameRanges('{}-{}'.format(first, last))
        nuke.render(review_node, ranges)

        # delete thumbnail network after render
        nuke.delete(review_node)

        # delete temporal write node
        if has_to_clean:
            nuke.delete(write_node)
        # restore selection
        nuke_utils.cleanSelection()
        for node in selected_nodes:
            node['selected'].setValue(True)

        component_name = options['component_name']
        return [temp_review_mov]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputReviewablePlugin(api_object)
    plugin.register()