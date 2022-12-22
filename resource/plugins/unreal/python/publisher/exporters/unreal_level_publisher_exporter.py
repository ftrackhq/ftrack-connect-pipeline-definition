# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)
from ftrack_connect_pipeline_unreal import plugin


class UnrealLevelPublisherExporterPlugin(plugin.UnrealPublisherExporterPlugin):
    '''Unreal file level exporter plugin'''

    plugin_name = 'unreal_level_publisher_exporter'

    @staticmethod
    def determine_extension(p):
        for ext in ['', '.uasset', '.umap']:
            result = '{}{}'.format(p, ext)
            if os.path.exists(result):
                return result
        raise Exception(
            'Could not determine asset "{}" files extension on disk!'.format(p)
        )

    def run(self, context_data=None, data=None, options=None):
        '''Retrieve the return the absolute level path on disk. The collected level path arrives at the form:

        /Game/FirstPerson/Maps/FirstPersonMap.FirstPersonMap
        '''

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        level_asset_path = (
            collected_objects[0].replace('/Game/', '').replace('/', os.sep)
        )
        level_deps = collected_objects[1:]

        root_content_dir = (
            unreal.SystemLibrary.get_project_content_directory().replace(
                '/', os.sep
            )
        )
        umap_path = self.determine_extension(
            os.path.join(root_content_dir, level_asset_path)
        )
        dependency_paths = [
            self.determine_extension(
                os.path.join(
                    root_content_dir,
                    p.replace('/Game/', '').replace('/', os.sep),
                )
            )
            for p in level_deps
        ]

        return [umap_path], {'data': dependency_paths}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    output_plugin = UnrealLevelPublisherExporterPlugin(api_object)
    output_plugin.register()
