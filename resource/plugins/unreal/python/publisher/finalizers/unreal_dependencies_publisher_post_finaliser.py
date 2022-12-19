# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealDependenciesPublisherFinalizerPlugin(
    plugin.UnrealPublisherPostFinalizerPlugin
):
    '''Plugin for finalizing the Unreal open process'''

    plugin_name = 'unreal_dependencies_publisher_post_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Publisher unreal asset dependencies to ftrack'''

        # TODO: Find collected dependencies and publish them to ftrack
        import json

        print('@@@ CONTEXT: {}'.format(json.dumps(context_data, indent=4)))
        print('@@@ DATA: {}'.format(json.dumps(data, indent=4)))
        print('@@@ OPTIONS: {}'.format(json.dumps(options, indent=4)))

        message = ''

        return (True, {'message': message})


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesPublisherFinalizerPlugin(api_object)
    plugin.register()
