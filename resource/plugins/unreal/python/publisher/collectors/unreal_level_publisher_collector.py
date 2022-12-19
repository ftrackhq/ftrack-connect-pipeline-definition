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
    '''Unreal level/script nodes publisher collector plugin'''

    plugin_name = 'unreal_level_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Collect Unreal level asset name, save it first.'''
        if not unreal.EditorLevelLibrary.save_current_level():
            error_message = "Error exporting the level: Please save the level with a name before publish"
            self.logger.error(error_message)
            return False, {'message': error_message}
        level_asset_path = str(
            unreal.EditorLevelLibrary.get_editor_world().get_path_name()
        ).split('.')[0]
        return [level_asset_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealLevelPublisherCollectorPlugin(api_object)
    plugin.register()
