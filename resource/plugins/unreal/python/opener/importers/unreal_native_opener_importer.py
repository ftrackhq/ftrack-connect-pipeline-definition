# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import copy
import os

import unreal

import ftrack_api

from ftrack_connect_pipeline.constants import asset as asset_const

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealNativeOpenerImporterPlugin(plugin.UnrealOpenerImporterPlugin):
    '''Unreal native importer plugin.'''

    plugin_name = 'unreal_native_opener_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Open an Unreal asset from path stored in collected object provided with *data*'''

        load_mode = load_const.OPEN_MODE
        load_mode_fn = self.load_modes.get(
            load_mode, list(self.load_modes.keys())[0]
        )

        # Pass version ID to enable evaluation of content browser path
        unreal_options = copy.deepcopy(options)
        unreal_options.update(
            {'version_id': context_data['version_id']}.items()
        )

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.append(
                collector['result'].get(asset_const.COMPONENT_PATH)
            )

        is_dependency = options.get('is_dependency') is True
        for component_path in paths_to_import:

            self.logger.debug(
                'Copy path to content folder: "{}"'.format(component_path)
            )
            asset_filesystem_path = load_mode_fn(
                component_path, unreal_options, self.session
            )

            # Restore any ftrack dependency asset info
            unreal_utils.import_ftrack_dependency_asset_info(
                context_data['version_id'],
                asset_filesystem_path,
                self.event_manager,
            )

            # Load dependencies
            objects_to_connect = None
            if not is_dependency:
                self.logger.debug('Loading dependencies')
                objects_to_connect = unreal_utils.import_dependencies(
                    context_data['version_id'], self.event_manager, self.logger
                )

            # Have Unreal discover the asset
            assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
            assetRegistry.scan_paths_synchronous(
                [os.path.dirname(asset_filesystem_path)], force_rescan=True
            )

            # Load the asset in Unreal
            asset_path = unreal_utils.filesystem_asset_path_to_asset_path(
                asset_filesystem_path
            )
            self.logger.debug(
                'Result of loading asset "{}" in Unreal editor: {}'.format(
                    asset_path,
                    unreal.EditorAssetLibrary.load_asset(asset_path),
                )
            )

            if objects_to_connect:
                self.logger.debug(
                    'Connecting {} dependencies'.format(
                        len(objects_to_connect)
                    )
                )
                for asset_path, asset_info in objects_to_connect:
                    unreal_utils.connect_object(
                        asset_path, asset_info, self.logger
                    )

            if not is_dependency:
                # Connect my self, cannot be done in plugin run as it will also detect
                # and connect dependencies
                self.ftrack_object_manager.connect_objects([asset_path])

            self.logger.debug(
                'Imported Unreal asset to: "{}"'.format(asset_filesystem_path)
            )

            results[component_path] = asset_filesystem_path

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealNativeOpenerImporterPlugin(api_object)
    plugin.register()
