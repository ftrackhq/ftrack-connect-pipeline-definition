# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

import unreal

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealLevelPublisherCollectorPlugin(
    plugin.UnrealPublisherCollectorPlugin
):
    '''Unreal level/assets publisher collector plugin'''

    plugin_name = 'unreal_dependencies_publisher_collector'

    def fetch(self, context_data=None, data=None, options=None):
        '''Fetch all dependencies from the level'''

        level_asset_path = (
            unreal.EditorLevelLibrary.get_editor_world().get_path_name()
        )

        return unreal_utils.get_asset_dependencies(level_asset_path)

    def run(self, context_data=None, data=None, options=None):
        '''Return the list of collected object from *options*'''
        unreal_objects = options.get('collected_objects', [])
        return unreal_objects


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealLevelPublisherCollectorPlugin(api_object)
    plugin.register()
