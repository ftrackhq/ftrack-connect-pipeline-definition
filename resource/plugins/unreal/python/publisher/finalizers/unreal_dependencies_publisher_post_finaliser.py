# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

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

        print('@@@ CONTEXT: {}'.format(json.dumps(context_data, indent=4)))
        print('@@@ DATA: {}'.format(json.dumps(data, indent=4)))
        print('@@@ OPTIONS: {}'.format(json.dumps(options, indent=4)))

        # Get the dependencies and the host ID from data
        dependencies = host_id = None
        for comp in data:
            if comp['name'] == 'snapshot':
                for result in comp['result']:
                    if result['name'] == 'exporter':
                        dependencies = result['user_data']['data']
                        host_id = result['host_id']
                        break
        if not dependencies:
            True, {'message': 'Could not find any dependencies to publish!'}

        # Build and send batch publisher event
        event = ftrack_api.event.base.Event(
            topic=core_constants.PIPELINE_CLIENT_LAUNCH,
            data={
                'pipeline': {
                    'host_id': host_id,
                    'name': core_constants.BATCH_PUBLISHER,
                    'title': 'Publishing dependencies',
                    'run': True,
                    'source': str(self),
                    'assets': dependencies,
                }
            },
        )
        self._event_manager.publish(
            event,
        )

        return True, {
            'message': 'Launched publish of dependencies in separate client'
        }


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesPublisherFinalizerPlugin(api_object)
    plugin.register()
