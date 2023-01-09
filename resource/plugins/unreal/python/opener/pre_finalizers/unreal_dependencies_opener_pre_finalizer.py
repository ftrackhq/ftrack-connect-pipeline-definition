# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealDependenciesOpenerPreFinalizerPlugin(
    plugin.UnrealOpenerPreFinalizerPlugin
):
    plugin_name = 'unreal_dependencies_opener_pre_finalizer'

    def run(self, context_data=None, data=None, options=None):
        ''''''

        result = {}

        print(
            '@@@ OPEN PRE FIN CONTEXT: {}'.format(
                json.dumps(context_data, indent=4)
            )
        )
        print('@@@ OPEN PRE FIN DATA: {}'.format(json.dumps(data, indent=4)))
        print(
            '@@@ OPEN PRE FIN OPTIONS: {}'.format(
                json.dumps(options, indent=4)
            )
        )

        # TODO: harvest dependencies from opened context

        self.logger.debug('Import asset/level dependencies in Unreal editor')
        # TODO: import dependencies in Unreal editor

        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesOpenerPreFinalizerPlugin(api_object)
    plugin.register()
