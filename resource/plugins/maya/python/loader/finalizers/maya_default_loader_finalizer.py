# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils
from ftrack_connect_pipeline_maya.constants.asset import modes as load_const


class MayaDefaultLoaderFinalizerPlugin(plugin.MayaLoaderFinalizerPlugin):
    plugin_name = 'maya_default_loader_finalizer'


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaDefaultLoaderFinalizerPlugin(api_object)
    plugin.register()