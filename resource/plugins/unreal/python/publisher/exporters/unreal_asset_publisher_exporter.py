# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)
from ftrack_connect_pipeline_unreal import plugin


class UnrealAssetPublisherExporterPlugin(plugin.UnrealPublisherExporterPlugin):
    '''Unreal file asset exporter plugin'''

    plugin_name = 'unreal_asset_publisher_exporter'

    def run(self, context_data=None, data=None, options=None):
        '''Retrieve the return the absolute asset path on disk. The collected asset path arrives at the form:

        /Game/FirstPerson/Maps/FirstPersonMap.FirstPersonMap
        '''

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        asset_asset_path = (
            collected_objects[0].replace('/Game/', '').replace('/', os.sep)
        )
        asset_dependencies = collected_objects[1:]

        root_content_dir = (
            unreal.SystemLibrary.get_project_content_directory().replace(
                '/', os.sep
            )
        )
        asset_path = unreal_utils.determine_extension(
            os.path.join(root_content_dir, asset_asset_path)
        )

        return [asset_path], {'data': asset_dependencies}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    output_plugin = UnrealAssetPublisherExporterPlugin(api_object)
    output_plugin.register()
