# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os.path

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline import constants as core_constants


class UnrealDependenciesPublisherFinalizerPlugin(
    plugin.UnrealPublisherPostFinalizerPlugin
):
    '''Plugin for finalizing the Unreal open process'''

    plugin_name = 'unreal_dependencies_publisher_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Publisher unreal asset dependencies to ftrack'''

        import json

        print(
            '@@@ PUB POST FIN CONTEXT: {}'.format(
                json.dumps(context_data, indent=4)
            )
        )
        print('@@@ PUB POST FIN DATA: {}'.format(json.dumps(data, indent=4)))
        print(
            '@@@ PUB POST FIN OPTIONS: {}'.format(
                json.dumps(options, indent=4)
            )
        )

        # Get the dependencies and the host ID from data
        dependencies = host_id = asset_version_id = asset_path = None
        for comp in data:
            if comp['name'] == 'snapshot':
                for result in comp['result']:
                    if result['name'] == 'exporter':
                        plugin_result = result['result'][0]
                        dependencies = plugin_result['user_data']['data']
                        host_id = plugin_result['host_id']
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

        if not dependencies:
            return {'message': 'No dependencies supplied for publish!'}

        pipeline_data = {
            'host_id': host_id,
            'name': core_constants.BATCH_PUBLISHER,
            'title': 'Publish level dependencies - {}'.format(
                os.path.basename(asset_path)
            ),
            'source': str(self),
            'assets': dependencies,
            'parent_asset_version_id': asset_version_id,
        }
        if not options.get('interactive') is False:
            # Build and send batch publisher spawn event
            event = ftrack_api.event.base.Event(
                topic=core_constants.PIPELINE_CLIENT_LAUNCH,
                data={'pipeline': pipeline_data},
            )
            self._event_manager.publish(
                event,
            )

            return {
                'message': 'Launched publish of dependencies with batch publisher client'
            }
        else:
            # Publish of dependencies are handled by the batch publisher, store data for pickup
            return {
                'message': 'Stored dependency data for pickup by batch publisher'
            }, {'data': pipeline_data}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesPublisherFinalizerPlugin(api_object)
    plugin.register()
