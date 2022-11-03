# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

# import maya.cmds as cmds

import ftrack_api

from ftrack_connect_pipeline_max import plugin


class MaxSelectionPublisherCollectorPlugin(plugin.MaxPublisherCollectorPlugin):
    plugin_name = 'max_selection_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Collect selected Max scene objects'''
        # selection = cmds.ls(sl=True)
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MaxSelectionPublisherCollectorPlugin(api_object)
    plugin.register()
