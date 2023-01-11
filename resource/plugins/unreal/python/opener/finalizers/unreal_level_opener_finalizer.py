# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json
import os
import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealLevelOpenerFinalizerPlugin(plugin.UnrealOpenerFinalizerPlugin):
    plugin_name = 'unreal_level_opener_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Open the level in Unreal Editor.'''

        result = {}

        # Find the path to level
        level_filesystem_path = None
        for comp in data:
            if comp['name'] == 'snapshot':
                for result in comp['result']:
                    if result['name'] == 'importer':
                        plugin_result = result['result'][0]
                        level_filesystem_path = list(
                            plugin_result['result'].values()
                        )[0]
                        break
        # Expect: "C:\\Users\\Henrik Norin\\Documents\\Unreal Projects\\MyEmptyProject\\Content\\Levels\\NewWorld.umap"
        # Transform to asset path
        root_content_dir = (
            unreal.SystemLibrary.get_project_content_directory().replace(
                '/', os.sep
            )
        )
        level_path = '/Game/{}'.format(
            level_filesystem_path[len(root_content_dir) :].replace('\\', '/')
        )

        self.logger.debug(
            'Opening level {} in Unreal editor'.format(level_path)
        )
        unreal.EditorLevelLibrary.load_level(level_path)

        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealLevelOpenerFinalizerPlugin(api_object)
    plugin.register()
