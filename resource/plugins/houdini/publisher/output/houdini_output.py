# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import tempfile
import os
import subprocess

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api



class OutputHoudiniPlugin(plugin.PublisherOutputHoudiniPlugin):

    extension = None
    filetype = None

    def run(self, context=None, data=None, options=None):
        component_name = options['component_name']

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=self.extension
        ).name

        if os.path.isfile(data[0]):
            hou.hipFile.save(new_file_path)
        else:

            hou.copyNodesToClipboard([hou.node(obj_name) for obj_name in data])

            command = "hou.pasteNodesFromClipboard(hou.node('/obj'));\
                            hou.hipFile.save('%s')" % (new_file_path.replace("\\","\\\\"))

            cmd = '%s -c "%s"' % (os.path.join(
                os.getenv('HFS'), 'bin', 'hython'), command)

            my_env = os.environ.copy()
            if 'HOUDINI_PATH' in my_env:
                del my_env['HOUDINI_PATH']
            subprocess.Popen(cmd, env=my_env)

            #os.system(cmd)

        return {component_name: new_file_path}


class OutputHoudiniHIPPlugin(OutputHoudiniPlugin):
    plugin_name = 'houdini_scene'
    extension = '.hip'
    filetype = 'hip'


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    hip_plugin = OutputHoudiniHIPPlugin(api_object)
    hip_plugin.register()
