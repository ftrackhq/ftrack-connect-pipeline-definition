# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class MayaSetPublisherCollectorPlugin(plugin.MayaPublisherCollectorPlugin):
    plugin_name = 'maya_set_publisher_collector'

    def run(self, context_data=None, data=None, options=None):

        set_name = options['set_name']
        return cmds.sets(set_name, q=True)


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaSetPublisherCollectorPlugin(api_object)
    plugin.register()