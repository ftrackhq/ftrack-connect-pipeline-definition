# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api
import os
import clique
import tempfile
import shutil

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils

import nuke


class OutputMoviePlugin(plugin.NukePublisherExporterPlugin):
    plugin_name = 'movie'

    def run(self, context_data=None, data=None, options=None):

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        node_name = collected_objects[0]
        input_node = nuke.toNode(node_name)
        selected_nodes = nuke.selectedNodes()
        nuke_utils.cleanSelection()

        try:
            mode = (options.get('mode') or 'render').lower()
            if mode == 'render' or mode == 'render_from_sequence':
                write_node = read_node = None
                delete_write_node = True
                delete_read_node = False
                if mode == 'render_from_sequence':
                    # Find sequence read/write node
                    file_node = None
                    for node in selected_nodes:
                        if node.Class() in ['Read', 'Write']:
                            # Is it a sequence?
                            if len(
                                node['file'].value() or ''
                            ) and not os.path.splitext(node['file'].value())[
                                1
                            ].lower() in [
                                '.mov',
                                '.mxf',
                            ]:
                                file_node = node
                                break
                    if file_node is None:
                        return (
                            False,
                            {
                                'message': 'No sequence write/read node selected!'
                            },
                        )
                    self.logger.debug(
                        'Using existing node {} file sequence path: "{}"'.format(
                            file_node.name(), file_node['file'].value()
                        )
                    )
                    if file_node.Class() in ['Write']:
                        # Read the sequence
                        read_node = nuke.createNode('Read')
                        read_node.setInput(0, input_node)
                        read_node['file'].fromUserText(
                            file_node['file'].value()
                        )
                        read_node['first'].setValue(file_node['first'].value())
                        read_node['last'].setValue(file_node['first'].value())
                        read_node['colorspace'].setValue(
                            file_node['colorspace'].value()
                        )
                        input_node = read_node
                        delete_read_node = True
                    else:
                        read_node = (
                            input_node
                        ) = file_node  # Use this read node during render
                write_node = nuke.createNode('Write')
                write_node.setInput(0, input_node)

                write_node['first'].setValue(
                    int(
                        float(
                            options.get('start_frame')
                            or nuke.root()['first_frame'].value()
                        )
                    )
                )
                write_node['last'].setValue(
                    int(
                        float(
                            options.get('end_frame')
                            or nuke.root()['last_frame'].value()
                        )
                    )
                )

                default_file_format = str(options.get('file_format'))
                selected_file_format = str(options.get('image_format'))
                default_file_format_options = options.get(
                    'file_format_options'
                )

                # Generate exporters file name for mov.
                temp_name = tempfile.NamedTemporaryFile()

                first = str(int(write_node['first'].getValue()))
                last = str(int(write_node['last'].getValue()))

                movie_path = '{}.{}'.format(
                    temp_name.name, selected_file_format
                )

                write_node['file'].setValue(movie_path.replace('\\', '/'))

                write_node['file_type'].setValue(selected_file_format)
                if len(options.get(selected_file_format) or {}) > 0:
                    for k, v in options[selected_file_format].items():
                        write_node[k].setValue(v)

                ranges = nuke.FrameRanges('{}-{}'.format(first, last))
                self.logger.debug(
                    'Rendering movie [{}-{}] to "{}"'.format(
                        first, last, movie_path
                    )
                )
                nuke.render(write_node, ranges)

                if delete_write_node:
                    # delete temporal write node
                    nuke.delete(write_node)
                if delete_read_node:
                    nuke.delete(read_node)
            else:
                # Find movie write/read node among selected nodes
                file_node = None
                for node in selected_nodes:
                    if node.Class() in ['Read', 'Write']:
                        # Is it a sequence?
                        if len(
                            node['file'].value() or ''
                        ) and os.path.splitext(node['file'].value())[
                            1
                        ].lower() in [
                            '.mov',
                            '.mxf',
                        ]:
                            file_node = node
                            break
                if file_node is None:
                    return (
                        False,
                        {'message': 'No movie write/read node selected!'},
                    )
                self.logger.debug(
                    'Using existing node {} movie path: "{}", copying to temp.'.format(
                        file_node.name(), file_node['file'].value()
                    )
                )

                # Make a copy of the file so it can be moved
                # Generate exporters file name for mov.
                movie_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.mov'
                ).name

                shutil.copy(file_node['file'].value(), movie_path)

        finally:
            # restore selection
            nuke_utils.cleanSelection()
            for node in selected_nodes:
                node['selected'].setValue(True)

        return [str(movie_path)]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputMoviePlugin(api_object)
    plugin.register()
