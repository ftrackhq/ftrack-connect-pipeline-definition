# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json
import os
import unreal

import ftrack_api

from ftrack_connect_pipeline import constants as core_constants
from ftrack_connect_pipeline.utils import load_pipeline_metadata, str_version
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
                        component_path = list(
                            plugin_result['result']['result'].keys()
                        )[0]
                        asset_filesystem_path = plugin_result['result'][
                            'result'
                        ][component_path]
                        break

        if asset_filesystem_path is None:
            # No asset path found, abort
            return {'message': 'No loaded asset path found.'}

        # Expect: "C:\\Users\\<user name>\\Documents\\Unreal Projects\\MyEmptyProject\\Content\\Assets\\NewWorld.umap"
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
        asset_version = self.session.query(
            'AssetVersion where id is "{}"'.format(context_data['version_id'])
        ).one()
        ident = str_version(asset_version, by_task=False)
        metadata = load_pipeline_metadata(asset_version)
        if metadata:
            metadata = json.loads(
                asset_version['metadata'][core_constants.PIPELINE_METADATA_KEY]
            )
            if core_constants.PIPELINE_ASSET_INFO_METADATA_KEY in metadata:
                asset_info = metadata[
                    core_constants.PIPELINE_ASSET_INFO_METADATA_KEY
                ]

                dependency_asset_version = self.session.query(
                    'AssetVersion where id is "{}"'.format(
                        asset_info[asset_const.VERSION_ID]
                    )
                ).one()
                dependency_ident = str_version(
                    dependency_asset_version, by_task=False
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
                    ftrack_object_manager.generate_dcc_object_name()
                )
                # Check if asset info is already present, need to remove it otherwise we won't be
                # able to restore it.
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
                # Remove metadata tag if carried along, no pipeline asset info restored
                if unreal_utils.conditional_remove_metadata_tag(
                    asset_path, asset_const.NODE_METADATA_TAG
                ):
                    self.logger.debug(
                        'Removed pipeline asset metadata tag from asset: {}'.format(
                            asset_path
                        )
                    )
        else:
            self.logger.debug('No metadata found for asset: {}'.format(ident))

        result['asset'] = asset_path

        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealAssetLoaderFinalizerPlugin(api_object)
    plugin.register()
