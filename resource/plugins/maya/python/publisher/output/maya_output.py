# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import tempfile
import os

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api



class OutputMayaPlugin(plugin.PublisherOutputMayaPlugin):

    extension = None
    filetype = None

    def extract_options(self, options):
        return {
            'op': 'v=0',
            'typ': self.filetype,
            'constructionHistory' : bool(options.get('history', False)),
            'channels' : bool(options.get('channels', False)),
            'preserveReferences' : bool(options.get('preserve_reference', False)),
            'shader' : bool(options.get('shaders', False)),
            'constraints' : bool(options.get('constraints', False)),
            'expressions' : bool(options.get('expressions', False)),
            'exportSelected': True,
            'exportAll': False,
            'force': True
        }

    def run(self, context_data=None, data=None, options=None):
        component_name = options['component_name']

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=self.extension
        ).name

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if os.path.isfile(collected_objects[0]):
            options = {
                'typ': self.filetype,
                'save': True
            }
            scene_name = cmds.file(q=True, sceneName=True)
            cmds.file(rename=new_file_path)
            cmds.file(**options)
            cmds.file(rename=scene_name)
        else:

            options = self.extract_options(options)

            self.logger.debug(
                'Calling output options: data {}. options {}'.format(
                    collected_objects, options
                )
            )
            cmds.select(collected_objects, r=True)
            cmds.file(
                new_file_path,
                **options
            )

        return [new_file_path]


class OutputMayaAsciiPlugin(OutputMayaPlugin):
    plugin_name = 'maya_ascii'
    extension = '.ma'
    filetype = 'mayaAscii'


class OutputMayaBinaryPlugin(OutputMayaPlugin):
    plugin_name = 'maya_binary'
    extension = '.mb'
    filetype = 'mayaBinary'


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    ma_plugin = OutputMayaAsciiPlugin(api_object)
    mb_plugin = OutputMayaBinaryPlugin(api_object)
    ma_plugin.register()
    mb_plugin.register()
