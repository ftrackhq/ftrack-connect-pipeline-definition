# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import traceback

import ftrack_api


from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealDependenciesOpenerPreFinalizerPlugin(
    plugin.UnrealOpenerPreFinalizerPlugin
):
    '''Unreal dependencies importer plugin.'''

    plugin_name = 'unreal_dependencies_opener_pre_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Recursively bring in all Unreal dependencies of the opened version.'''

        try:
            messages = unreal_utils.import_dependencies(
                context_data['version_id'], self.event_manager, self.logger
            )
            return {'message': ';'.join(messages)}
        except:
            print(traceback.format_exc())
            self.logger.warning(traceback.format_exc())
            raise


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesOpenerPreFinalizerPlugin(api_object)
    plugin.register()
