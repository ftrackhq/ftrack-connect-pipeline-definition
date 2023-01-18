# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os.path

import ftrack_api

from ftrack_connect_pipeline import constants as core_constants
from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_qt import constants as qt_constants

from ftrack_connect_pipeline_unreal import utils as unreal_utils

class UnrealAssetInfoPublisherFinalizerPlugin(
    plugin.UnrealPublisherPostFinalizerPlugin
):
    '''Plugin for finalizing the Unreal asset info publish process'''

    plugin_name = 'unreal_assetinfo_publisher_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Publish the non snapshot asset info to ftrack if exists'''

        # Extract version ID from the run data
        asset_version_id = asset_path = None
        for comp in data:
            if comp['name'] == 'snapshot':
                for result in comp['result']:
                    if result['name'] == 'exporter':
                        asset_path = plugin_result['result'][0]
                        break
            elif comp['name'] == 'main':
                for result in comp['result']:
                    if result['name'] == 'finalizer':
                        plugin_result = result['result'][0]
                        asset_version_id = plugin_result['result'][
                            'asset_version_id'
                        ]
                        break

        if not asset_path:
            return {'message': 'No asset could be extracted from publish!'}

        unused_dcc_object_node, param_dict = unreal_utils.get_asset_info(asset_path)

        if param_dict:
            # Store the asset info as metadata in ftrack
            assetversion = self.session.query(
                'AssetVersion where id is "{0}"'.format(asset_version_id)
            ).one()
            if 'ftrack-connect-pipeline-unreal' in assetversion.get('metadata'):
                metadata = assetversion['metadata']['ftrack-connect-pipeline-unreal']

            assetversion['metadata'] =

        return {
            'message': 'Launched publish of assetinfo with batch publisher client'
        }


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealAssetInfoPublisherFinalizerPlugin(api_object)
    plugin.register()
