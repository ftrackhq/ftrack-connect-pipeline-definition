# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils
from ftrack_connect_pipeline_nuke.constants.asset import modes as load_const


class NukeDefaultLoaderFinalizerPlugin(plugin.NukeLoaderFinalizerPlugin):
    plugin_name = 'nuke_default_loader_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Default Nuke loader finalizer plugin'''
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeDefaultLoaderFinalizerPlugin(api_object)
    plugin.register()
