# :coding: utf-8
# :copyright: Copyright (c) 2014-2023 ftrack
import os
import copy

import unreal

from ftrack_connect_pipeline.constants import asset as asset_const

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
import ftrack_api


class UnrealAssetLoaderImporterPlugin(plugin.UnrealLoaderImporterPlugin):
    '''Unreal asset loader plugin'''

    plugin_name = 'unreal_asset_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Load an Unreal asset from path stored in collected object provided with *data*'''

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

        for component_path in paths_to_import:
            self.logger.debug('Loading path: "{}"'.format(component_path))

            asset_filesystem_path = load_mode_fn(
                component_path, unreal_options, self.session
            )

            # Align modification date so asset does not appear as out of sync, after load
            # the local asset info will have the modification date of the imported asset
            # within ftrack location
            file_size_remote = os.path.getsize(component_path)
            file_size_local = os.path.getsize(asset_filesystem_path)
            mod_date_remote = os.path.getmtime(component_path)

            stat = os.stat(asset_filesystem_path)
            os.utime(
                asset_filesystem_path, times=(stat.st_atime, mod_date_remote)
            )
            self.logger.debug(
                'Restored file modification time: {} on asset: {} (size: {}, local size: {})'.format(
                    mod_date_remote,
                    asset_filesystem_path,
                    file_size_remote,
                    file_size_local,
                )
            )

            # Have Unreal discover the newly imported asset
            assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
            assetRegistry.scan_paths_synchronous(
                [os.path.dirname(asset_filesystem_path)], force_rescan=True
            )

            self.logger.debug(
                'Imported asset to: "{}"'.format(asset_filesystem_path)
            )

            results[component_path] = asset_filesystem_path

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealAssetLoaderImporterPlugin(api_object)
    plugin.register()
