# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json

import ftrack_api

from ftrack_connect_pipeline import constants as core_constants
from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_qt import constants as qt_constants

from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealDependencyTrackPublisherFinalizerPlugin(
    plugin.UnrealPublisherPostFinalizerPlugin
):
    '''Plugin for finalizing the Unreal publish process for a dependency'''

    plugin_name = 'unreal_dependencytrack_publisher_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Create/update local snapshot asset info'''

        import json

        print(
            '@@@ UnrealDependencyTrackPublisherFinalizerPlugin.run(): context_data = {}'.format(
                json.dumps(context_data, indent=4)
            )
        )

        print(
            '@@@ UnrealDependencyTrackPublisherFinalizerPlugin.run(): data = {}'.format(
                json.dumps(data, indent=4)
            )
        )

        # Extract version ID from the run data
        asset_version_id = component_name = asset_filesystem_path = None
        for comp in data:
            if comp['type'] == core_constants.COMPONENT:
                for result in comp['result']:
                    if result['name'] == core_constants.EXPORTER:
                        plugin_result = result['result'][0]
                        asset_filesystem_path = plugin_result['result'][0]
                        break
            elif comp['type'] == core_constants.FINALIZER:
                for result in comp['result']:
                    if result['name'] == core_constants.FINALIZER:
                        plugin_result = result['result'][0]
                        asset_version_id = plugin_result['result'][
                            'asset_version_id'
                        ]
                        for component_name in plugin_result['result'][
                            'component_names'
                        ]:
                            if not component_name in [
                                'thumbnail',
                                'reviewable',
                            ]:
                                break
                        break

        if 'asset_path' in options:
            # Given pre fetched by batch publisher
            asset_path = options['asset_path']
            param_dict = options['param_dict']
            dcc_object_name = options['dcc_object_name']
        else:
            if not asset_filesystem_path:
                return {'message': 'No asset could be extracted from publish!'}

            # Convert to game path
            asset_path = unreal_utils.filesystem_asset_path_to_asset_path(
                asset_filesystem_path
            )

            # Check if already has snapshot asset info
            dcc_object_name, param_dict = unreal_utils.get_asset_info(
                asset_path, snapshot=True
            )

        if param_dict:
            # Store the asset info as metadata in ftrack
            self.logger.warning(
                'Removing existing snapshot asset info @ "{}"!'.format(
                    param_dict
                )
            )
            unreal_utils.delete_ftrack_node(dcc_object_name)

        # Create new snapshot asset info
        component = self.session.query(
            'Component where version.id is {} and name is "{}"'.format(
                asset_version_id, component_name
            )
        ).one()
        ftrack_object_manager = self.FtrackObjectManager(self.event_manager)
        ftrack_object_manager.asset_info = (
            ftrack_object_manager.generate_snapshot_asset_info(
                context_data,
                asset_version_id,
                component['id'],
                component_name,
                asset_filesystem_path,
            )
        )

        # Store asset info with Unreal project
        dcc_object = self.DccObject(
            name=ftrack_object_manager._generate_dcc_object_name()
        )
        ftrack_object_manager.dcc_object = dcc_object
        # Connect to existing dependency
        ftrack_object_manager.connect_objects([asset_path])

        message = 'Stored snapshot asset info {} for asset "{}"'.format(
            json.dumps(ftrack_object_manager.asset_info, indent=4), asset_path
        )
        self.logger.debug(message)
        return {'message': message}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependencyTrackPublisherFinalizerPlugin(api_object)
    plugin.register()
