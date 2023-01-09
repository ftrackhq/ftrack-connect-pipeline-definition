# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import json

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealLevelOpenerFinalizerPlugin(plugin.UnrealOpenerFinalizerPlugin):
    plugin_name = 'unreal_level_opener_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Save opened Unreal scene in temp to avoid being overwritten'''

        result = {}

        print('@@@ OPEN FIN CONTEXT: {}'.format(context_data))
        print('@@@ OPEN FIN DATA: {}'.format(json.dumps(data, indent=4)))
        print('@@@ OPEN FIN OPTIONS: {}'.format(json.dumps(options, indent=4)))

        self.logger.debug('Opening level in Unreal editor')
        # TODO: open level in Unreal editor

        return result


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealLevelOpenerFinalizerPlugin(api_object)
    plugin.register()
