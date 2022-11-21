# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

# import maya.cmds as cmds

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin


class UnrealSelectionPublisherCollectorPlugin(
    plugin.UnrealPublisherCollectorPlugin
):
    plugin_name = 'unreal_selection_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Collect selected Unreal scene objects'''
        # selection = cmds.ls(sl=True)
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealSelectionPublisherCollectorPlugin(api_object)
    plugin.register()
