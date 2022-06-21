# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import tempfile
import os

import maya.cmds as cmds

from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils
from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class MayaDefaultPublisherExporterPlugin(plugin.MayaPublisherExporterPlugin):
    plugin_name = 'maya_default_publisher_exporter'

    extension = None
    filetype = None

    def extract_options(self, options):
        return {
            'op': 'v=0',
            'typ': self.filetype,
            'constructionHistory': bool(options.get('history', False)),
            'channels': bool(options.get('channels', False)),
            'preserveReferences': bool(
                options.get('preserve_reference', False)
            ),
            'shader': bool(options.get('shaders', False)),
            'constraints': bool(options.get('constraints', False)),
            'expressions': bool(options.get('expressions', False)),
            'exportSelected': True,
            'exportAll': False,
            'force': True,
        }

    def run(self, context_data=None, data=None, options=None):

        self.filetype = options.get('file_type') or 'mayaBinary'
        self.extension = '.mb' if self.filetype is 'mayaBinary' else '.ma'

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=self.extension
        ).name

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if os.path.isfile(collected_objects[0]):
            # Save entire scene
            options = {'typ': self.filetype, 'save': True}
            scene_name = cmds.file(q=True, sceneName=True)
            if len(scene_name or '') == 0:
                # Scene is not saved, save it first. Should have been taken
                # care of by scene collector.
                self.logger.warning('Maya not saved, saving locally..')
                save_path, message = maya_utils.save(
                    context_data['context_id'], self.session, temp=True
                )
                if not message is None:
                    self.logger.info(message)
                scene_name = cmds.file(q=True, sceneName=True)

            cmds.file(rename=new_file_path)
            cmds.file(**options)
            cmds.file(rename=scene_name)
        else:
            # Export a subset of the scene
            options = self.extract_options(options)
            self.logger.debug(
                'Calling exporters options: data {}. options {}'.format(
                    collected_objects, options
                )
            )
            cmds.select(collected_objects, r=True)
            cmds.file(new_file_path, **options)

        return [new_file_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    output_plugin = MayaDefaultPublisherExporterPlugin(api_object)
    output_plugin.register()
