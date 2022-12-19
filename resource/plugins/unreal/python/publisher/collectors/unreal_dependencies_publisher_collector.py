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
        '''Fetch all cameras from the scene'''

        print("Data on the fetch call ---> {}".format(data))
        # TODO: take the level from the previous collector plugin executed

        level_asset_path = (
            unreal.EditorLevelLibrary.get_editor_world().get_path_name()
        )

        # https://docs.unrealengine.com/4.27/en-US/PythonAPI/class/AssetRegistry.html?highlight=assetregistry#unreal.AssetRegistry.get_dependencies
        # Setup dependency options
        dep_options = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True,
            include_hard_package_references=True,
            include_searchable_names=False,
            include_soft_management_references=True,
            include_hard_management_references=True,
        )
        # Start asset registry
        asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
        # Get dependencies from the level
        dependencies = [
            str(dep)
            for dep in asset_reg.get_dependencies(
                level_asset_path.split('.')[0], dep_options
            )
        ]

        # Filter out only dependencies that are in Game
        game_dependencies = list(
            filter(lambda x: x.startswith("/Game"), dependencies)
        )

        # TODO: Filter out dependencies that are in sync with ftrack

        return game_dependencies

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
