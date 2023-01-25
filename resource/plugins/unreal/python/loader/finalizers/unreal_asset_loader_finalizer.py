# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json
import os.path

import unreal

import ftrack_api

from ftrack_connect_pipeline import constants as core_constants
from ftrack_connect_pipeline.utils import str_version
from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)
from ftrack_connect_pipeline_unreal.constants import asset as asset_const
from ftrack_connect_pipeline_unreal.asset import UnrealFtrackObjectManager
from ftrack_connect_pipeline_unreal.asset.dcc_object import UnrealDccObject


class UnrealAssetLoaderFinalizerPlugin(plugin.UnrealLoaderFinalizerPlugin):
    '''Unreal asset load finalizer plugin.'''

    plugin_name = 'unreal_asset_loader_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Restore asset info.'''

        result = {}

        # First, evaluate asset path
        asset_filesystem_path = None
        for comp in data:
            if comp['type'] == core_constants.COMPONENT:
                for result in comp['result']:
                    if result['type'] == core_constants.IMPORTER:
                        plugin_result = result['result'][0]
                        asset_filesystem_path = list(
                            plugin_result['result']['result'].values()
                        )[0]
                        break

        if asset_filesystem_path is None:
            # No asset path found, abort
            return {'message': 'No loaded asset path found.'}

        # Expect: "C:\\Users\\Henrik Norin\\Documents\\Unreal Projects\\MyEmptyProject\\Content\\Assets\\NewWorld.umap"
        # Transform to asset path
        asset_path = unreal_utils.filesystem_asset_path_to_asset_path(
            asset_filesystem_path
        )

        # Load the asset in Unreal
        self.logger.debug(
            'Result of loading asset "{}" in Unreal editor: {}'.format(
                asset_path, unreal.EditorAssetLibrary.load_asset(asset_path)
            )
        )

        # Restore pipeline asset info
        assetversion = self.session.query(
            'AssetVersion where id is "{}"'.format(context_data['version_id'])
        ).one()
        ident = str_version(assetversion, by_task=False)
        metadata = None
        if 'ftrack-connect-pipeline-unreal' in assetversion['metadata']:
            metadata = json.loads(
                assetversion['metadata']['ftrack-connect-pipeline-unreal']
            )
            if 'pipeline_asset_info' in metadata:
                asset_info = metadata['pipeline_asset_info']

                dependency_assetversion = self.session.query(
                    'AssetVersion where id is "{}"'.format(
                        asset_info[asset_const.VERSION_ID]
                    )
                ).one()
                dependency_ident = str_version(
                    dependency_assetversion, by_task=False
                )
                self.logger.debug(
                    'Restoring pipeline asset info for {}: {}'.format(
                        dependency_ident, asset_info
                    )
                )
                ftrack_object_manager = UnrealFtrackObjectManager(
                    self.event_manager
                )
                ftrack_object_manager.asset_info = asset_info
                dcc_object = UnrealDccObject()
                dcc_object.name = (
                    ftrack_object_manager._generate_dcc_object_name()
                )
                if dcc_object.exists():
                    self.logger.debug(
                        'Pipeline asset {} already tracked in Unreal, removing!'.format(
                            dependency_ident
                        )
                    )
                    unreal_utils.delete_ftrack_node(dcc_object.name)
                # Store asset info
                dcc_object.create(dcc_object.name)
                # Have it sync to disk
                ftrack_object_manager.dcc_object = dcc_object
            else:
                # Remove metadata
                if unreal_utils.conditional_remove_metadata_tag(
                    asset_path, asset_const.NODE_METADATA_TAG
                ):
                    self.logger.debug(
                        'Removed pipeline asset metadata tag from asset: {}'.format(
                            asset_path
                        )
                    )
        # Remove snapshot metadata tag carried along - this is not a dependency (yet)
        if unreal_utils.conditional_remove_metadata_tag(
            asset_path, asset_const.NODE_SNAPSHOT_METADATA_TAG
        ):
            self.logger.debug(
                'Removed snapshot asset metadata tag from asset: {}'.format(
                    asset_path
                )
            )

        # Restore file modification time if possible
        if metadata is not None:
            if asset_const.FILE_SIZE in metadata:
                file_size = metadata[asset_const.FILE_SIZE]
                imported_file_size = os.path.getsize(asset_filesystem_path)
                mode_date = metadata[asset_const.MOD_DATE]
                if file_size == imported_file_size:
                    # Same size, lets assume it is the same file
                    stat = os.stat(asset_filesystem_path)
                    os.utime(
                        asset_filesystem_path, times=(stat.st_atime, mode_date)
                    )
                    self.logger.debug(
                        'Restored file modification time: {} on asset: {} (size: {})'.format(
                            mode_date, asset_path, file_size
                        )
                    )
                else:
                    self.logger.debug(
                        'Not restoring file modification time on asset {} - size differs! (at publish: {}, now: {})'.format(
                            asset_path, file_size, imported_file_size
                        )
                    )
            else:
                self.logger.debug(
                    'Not able to restore modification date - no file size metadata found on asset version: {}'.format(
                        ident
                    )
                )
        else:
            self.logger.debug(
                'Not able to restore modification date - no metadata found on asset version: {}'.format(
                    ident
                )
            )

        result['asset'] = asset_path

        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealAssetLoaderFinalizerPlugin(api_object)
    plugin.register()
