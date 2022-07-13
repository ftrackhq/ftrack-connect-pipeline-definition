# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import tempfile
import os
import subprocess

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class OutputHoudiniScenePlugin(plugin.PublisherOutputHoudiniPlugin):
    plugin_name = 'houdini_scene_output'
    extension = '.hip'
    filetype = 'hip'

    def run(self, context_data=None, data=None, options=None):

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=self.extension
        ).name

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if os.path.isfile(collected_objects[0]) or collected_objects[
            0
        ].endswith('.hip'):
            # Export entire scene
            hou.hipFile.save(new_file_path)
        else:
            # Export selected
            hou.copyNodesToClipboard(
                [hou.node(obj_path) for obj_path in collected_objects]
            )

            command = "hou.pasteNodesFromClipboard(hou.node('/obj'));\
                            hou.hipFile.save('{}')".format(
                new_file_path.replace("\\", "\\\\")
            )

            cmd = [
                os.path.join(os.getenv('HFS'), 'bin', 'hython'),
                '-c',
                command,
            ]

            my_env = os.environ.copy()
            if 'HOUDINI_PATH' in my_env:
                del my_env['HOUDINI_PATH']

            self.logger.debug(
                'Exporting scene with command: "{}".'.format(cmd)
            )

            subprocess.Popen(cmd, env=my_env)

        return [new_file_path]


class OutputHoudiniNodesPlugin(plugin.PublisherOutputHoudiniPlugin):
    plugin_name = 'houdini_nodes_output'
    extension = '.hip'
    filetype = 'hip'

    def run(self, context_data=None, data=None, options=None):

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=self.extension
        ).name

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if len(collected_objects) == 0:
            self.logger.debug('Saving scene to: "{}".'.format(new_file_path))

            hou.hipFile.save(new_file_path)
        else:

            hou.copyNodesToClipboard(
                [hou.node(obj_path) for obj_path in collected_objects]
            )

            command = "hou.pasteNodesFromClipboard(hou.node('/obj'));\
                            hou.hipFile.save('{}')".format(
                new_file_path.replace("\\", "\\\\")
            )

            cmd = [
                os.path.join(os.getenv('HFS'), 'bin', 'hython'),
                '-c',
                command,
            ]

            my_env = os.environ.copy()
            if 'HOUDINI_PATH' in my_env:
                del my_env['HOUDINI_PATH']

            self.logger.debug(
                'Exporting selected nodes with command: ' '"{}".'.format(cmd)
            )

            result = subprocess.Popen(cmd, env=my_env)
            result.communicate()
            if result.returncode != 0:
                raise Exception('Houdini selected nodes scene export failed!')

        return [new_file_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    scene_plugin = OutputHoudiniScenePlugin(api_object)
    scene_plugin.register()

    nodes_plugin = OutputHoudiniNodesPlugin(api_object)
    nodes_plugin.register()
